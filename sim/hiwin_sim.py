"""Event simulator of XAU_HiWin_EA_DUAL_LEAN_v40 (v39 = set atr_hard_min_pct=0, b_atr_min_pct=0) on Dukascopy M1 bid/ask data.

It reproduces the EA's OnTick order of operations. Inside each M1 candle the
price visits 4 points: open, then low/high (low first on a rising candle,
high first on a falling one), then close. Stops, targets and limit orders
fill at their own price when crossed, or at the gap price.

This is an approximation of MT5 "every tick based on real ticks": it is
calibrated against the v39 tester report before any result is trusted.
"""
import datetime as dt
import math
from dataclasses import dataclass, field

import numpy as np

from . import indicators as ind
from .data import resample

DEFAULTS = dict(
    tp_atr=0.5, sl_atr=5.0, time_stop_bars=48, max_spread_atr=0.10,
    start_hour=7, end_hour=21, limit_atr=0.3, limit_wait_bars=3,
    holidays=('2026.12.24', '2026.12.25', '2026.12.26', '2026.12.31', '2027.01.01'),
    use_s1=True, use_s5=True, ichi_shift=26, bb_period=20, bb_dev=2.0, extreme_bars=12,
    use_b1=True, b_lookback=20, b_spike_min=1.8, b_atr_min=5.0, b_sl_atr=1.5, b_tp_atr=6.0,
    b_trail_start=1.5, b_trail_atr=1.5, b_max_pos=2, b_lot_mult=1.0, b_cooldown=12,
    adx_min=12.0, range_bars=12, range_min_atr=2.0,
    atr_min_fixed=6.3, atr_lookback=576, atr_pctile=20.0, atr_hard_min=5.5, atr_hard_min_pct=0.12, b_atr_min_pct=0.11, spike_mult=1.5,
    lot_per_1000=0.01, fixed_lot=0.0, max_lot=5.0, max_margin_pct=30.0, max_loss_at_min_lot=5.0,
    recover_at_atr=2.0, recover_tp_atr=0.75, recover_lot_mult=1.0, group_stop_atr=0.0,
    max_positions=2, friday_filter=True, friday_stop_hour=20,
    max_open_risk_pct=20.0, daily_loss_pct=10.0, emergency_float_pct=25.0,
    recover_spike_guard=True, recover_hours_only=True,
    commission_per_lot_side=3.0, leverage=100.0, contract=100.0,
    use_ldn=False, ldn_start=3, ldn_end=9, ldn_close=21, ldn_tp=1.0, ldn_lot_mult=0.5,
    deposit=5000.0,
)


@dataclass
class Pos:
    id: int
    tag: str
    buy: bool
    lots: float
    op: float
    sl: float
    tp: float
    t_open: int
    atr_e: float          # ATR at entry (scalper: |op-sl|/sl_atr ; B1: its own)
    parent: int = 0       # recovery legs: id of the original
    mae: float = 0.0
    mfe: float = 0.0


@dataclass
class Pend:
    id: int
    tag: str
    buy: bool
    lots: float
    px: float
    sl: float
    tp: float
    t_setup: int


@dataclass
class Trade:
    id: int
    tag: str
    buy: bool
    lots: float
    op: float
    cp: float
    t_open: int
    t_close: int
    net: float
    exit: str
    atr_e: float
    parent: int
    mae: float
    mfe: float


class Sim:
    def __init__(self, m1, p=None):
        self.p = dict(DEFAULTS, **(p or {}))
        self.m1 = m1
        self._prep()

    # ------------------------------------------------------------------ indicators
    def _prep(self):
        P = self.p
        m1 = self.m1
        b5 = resample(m1, 5)
        self.b5 = b5
        h, l, c = b5['h'], b5['l'], b5['c']
        self.atr = ind.atr(h, l, c, 14)
        self.adx = ind.adx(h, l, c, 14)
        self.bbu, self.bbl = ind.bands(c, P['bb_period'], P['bb_dev'])
        self.spa, self.spb = ind.ichimoku_spans(h, l)
        sh = P['ichi_shift']
        if sh:   # value plotted at bar i was computed `sh` bars earlier
            self.spa = np.concatenate((np.full(sh, np.nan), self.spa[:-sh]))
            self.spb = np.concatenate((np.full(sh, np.nan), self.spb[:-sh]))
        b15 = resample(m1, 15)
        self.b15 = b15
        self.e20 = ind.ema(b15['c'], 20)
        self.e50 = ind.ema(b15['c'], 50)
        # M5 bar index -> index of the M15 bar that contains its open time
        self.m15_of_m5 = np.searchsorted(b15['t'], b5['t'], side='right') - 1
        # rolling helpers on M5
        n = len(c)
        self.atr_avg50 = np.full(n, np.nan)       # average of atr[2..51] seen from bar0 = i -> bars i-2..i-51
        cs = np.cumsum(np.insert(np.nan_to_num(self.atr), 0, 0.0))
        for i in range(52, n):
            self.atr_avg50[i] = (cs[i - 1] - cs[i - 51]) / 50.0
        self.m5_of_m1 = np.searchsorted(b5['t'], m1['t'], side='right') - 1

    def trend(self, k):
        """TrendDir() at new M5 bar k (bar0 = k). M15 shift 1 = bar before the one containing now."""
        j = self.m15_of_m5[k] - 1
        if j < 5:
            return 0
        f1, s1, s4, c = self.e20[j], self.e50[j], self.e50[j - 3], self.b15['c'][j]
        if f1 > s1 and s1 > s4 and c > s1:
            return 1
        if f1 < s1 and s1 < s4 and c < s1:
            return -1
        return 0

    # ------------------------------------------------------------------ helpers
    def equity(self, bid, ask):
        return self.balance + sum(self.pl(x, bid, ask) for x in self.pos)

    def pl(self, x, bid, ask):
        cs = self.p['contract']
        return ((bid - x.op) if x.buy else (x.op - ask)) * x.lots * cs

    def used_margin(self, price):
        return sum(x.lots * self.p['contract'] * x.op / self.p['leverage'] for x in self.pos)

    def calc_lot(self, entry, sl_dist, bid, ask):
        P = self.p
        eq = self.equity(bid, ask)
        lpl = sl_dist * P['contract']
        if P['fixed_lot'] > 0:
            lot = P['fixed_lot']
        else:
            lot = eq / 1000.0 * P['lot_per_1000']
        lot = math.floor(lot / 0.01 + 1e-9) * 0.01
        if lot < 0.01:
            if lpl * 0.01 > eq * P['max_loss_at_min_lot'] / 100.0:
                return 0.0
            lot = 0.01
        lot = min(lot, P['max_lot'])
        free = eq - self.used_margin(entry)
        m = lot * P['contract'] * entry / P['leverage']
        cap = free * P['max_margin_pct'] / 100.0
        if m > cap:
            lot = math.floor(lot * cap / m / 0.01 + 1e-9) * 0.01
            if lot < 0.01:
                return 0.0
        return round(lot, 2)

    def open_risk_pct(self, bid, ask):
        eq = self.equity(bid, ask)
        if eq <= 0:
            return 0.0
        r = 0.0
        for x in self.pos:
            loss = (x.op - x.sl) if x.buy else (x.sl - x.op)
            if x.sl > 0 and loss > 0:
                r += loss * x.lots * self.p['contract']
        return r / eq * 100.0

    def in_window(self, t):
        d = dt.datetime.utcfromtimestamp(t)
        P = self.p
        if P['friday_filter'] and d.weekday() == 4 and d.hour >= P['friday_stop_hour']:
            return False
        return P['start_hour'] <= d.hour <= P['end_hour']

    def is_holiday(self, t):
        return dt.datetime.utcfromtimestamp(t).strftime('%Y.%m.%d') in self.p['holidays']

    def spike_now(self, k):
        P = self.p
        if P['spike_mult'] <= 0 or k < 52:
            return False
        return self.atr[k - 1] > P['spike_mult'] * self.atr_avg50[k]

    # ------------------------------------------------------------------ position ops
    def _comm(self, lots):
        return lots * self.p['commission_per_lot_side']

    def open_pos(self, tag, buy, lots, price, sl, tp, t, atr_e, parent=0):
        self.nid += 1
        self.balance -= self._comm(lots)
        x = Pos(self.nid, tag, buy, lots, price, sl, tp, t, atr_e, parent)
        self.pos.append(x)
        return x

    def close_pos(self, x, price, t, why):
        cs = self.p['contract']
        g = ((price - x.op) if x.buy else (x.op - price)) * x.lots * cs
        self.balance += g - self._comm(x.lots)
        self.pos.remove(x)
        self.trades.append(Trade(x.id, x.tag, x.buy, x.lots, x.op, price, x.t_open, t,
                                 g - 2 * self._comm(x.lots), why, x.atr_e, x.parent, x.mae, x.mfe))

    # ------------------------------------------------------------------ main loop
    def run(self):
        P = self.p
        m1 = self.m1
        self.balance = P['deposit']
        self.pos, self.pend, self.trades = [], [], []
        self.nid = 0
        self.day = None
        self.day_start = self.balance
        self.locked = False
        self.last_break = -10**12
        self.ldn_day = None
        self.k_loaded = -1
        last_k = -1
        self.eq_curve = []
        bo, bh, bl, bc = m1['bo'], m1['bh'], m1['bl'], m1['bc']
        ao, ah, al, ac = m1['ao'], m1['ah'], m1['al'], m1['ac']
        T = m1['t']
        for j in range(len(T)):
            k = self.m5_of_m1[j]
            if bc[j] >= bo[j]:
                path = ((bo[j], ao[j]), (bl[j], al[j]), (bh[j], ah[j]), (bc[j], ac[j]))
            else:
                path = ((bo[j], ao[j]), (bh[j], ah[j]), (bl[j], al[j]), (bc[j], ac[j]))
            t = int(T[j])
            for pi, (bid, ask) in enumerate(path):
                tt = t + pi * 15
                self.broker(bid, ask, tt, gap=(pi == 0))
                newbar = (pi == 0 and k != last_k)
                self.on_tick(bid, ask, tt, k, newbar)
                if newbar:
                    last_k = k
            if j + 1 == len(T) or (T[j + 1] // 86400 != T[j] // 86400):
                self.eq_curve.append((t, self.balance, self.equity(bc[j], ac[j])))
        # close what is left at the last price
        for x in list(self.pos):
            self.close_pos(x, bc[-1] if x.buy else ac[-1], int(T[-1]), 'end')
        return self.trades

    # broker side: limit fills, stop and target hits
    def broker(self, bid, ask, t, gap):
        for o in list(self.pend):
            hit = (ask <= o.px) if o.buy else (bid >= o.px)
            if hit:
                fill = o.px
                self.pend.remove(o)
                self.open_pos(o.tag, o.buy, o.lots, fill, o.sl, o.tp, t,
                              abs(fill - o.sl) / self.p['sl_atr'])
        for x in list(self.pos):
            px = bid if x.buy else ask
            adv = (x.op - px) if x.buy else (px - x.op)
            fav = -adv
            x.mae = max(x.mae, adv)
            x.mfe = max(x.mfe, fav)
            if x.buy:
                if x.sl > 0 and bid <= x.sl:
                    self.close_pos(x, bid if gap else x.sl, t, 'sl')
                elif x.tp > 0 and bid >= x.tp:
                    self.close_pos(x, bid if gap else x.tp, t, 'tp')
            else:
                if x.sl > 0 and ask >= x.sl:
                    self.close_pos(x, ask if gap else x.sl, t, 'sl')
                elif x.tp > 0 and ask <= x.tp:
                    self.close_pos(x, ask if gap else x.tp, t, 'tp')

    def on_tick(self, bid, ask, t, k, newbar):
        P = self.p
        # ---- UpdateDay
        day = t // 86400
        if day != self.day:
            self.day = day
            self.day_start = self.balance
            self.locked = False
        elif P['daily_loss_pct'] > 0 and not self.locked and \
                self.day_start - self.balance >= self.day_start * P['daily_loss_pct'] / 100.0:
            self.locked = True
        if self.pos:
            # ---- emergency
            if P['emergency_float_pct'] > 0:
                eq = self.equity(bid, ask)
                fl = eq - self.balance
                if eq > 0 and fl < 0 and -fl / eq * 100 >= P['emergency_float_pct']:
                    for x in list(self.pos):
                        self.close_pos(x, bid if x.buy else ask, t, 'emergency')
                    self.locked = True
            # ---- time stop (not B1)
            for x in list(self.pos):
                if x.tag not in ('B1', 'L1') and t - x.t_open >= P['time_stop_bars'] * 300:
                    self.close_pos(x, bid if x.buy else ask, t, 'time')
            # ---- engine L closes at its hour
            if P['use_ldn'] and (t % 86400) // 3600 >= P['ldn_close']:
                for x in list(self.pos):
                    if x.tag == 'L1':
                        self.close_pos(x, bid if x.buy else ask, t, 'ldn_close')
            # ---- B1 trailing (atr from the last loaded bar)
            if P['use_b1'] and self.k_loaded > 0:
                a = self.atr[self.k_loaded - 1]
                for x in self.pos:
                    if x.tag != 'B1':
                        continue
                    cur = bid if x.buy else ask
                    prof = (cur - x.op) if x.buy else (x.op - cur)
                    if prof < P['b_trail_start'] * a:
                        continue
                    want = round(cur - P['b_trail_atr'] * a if x.buy else cur + P['b_trail_atr'] * a, 2)
                    if x.buy and want > x.sl + 0.01:
                        x.sl = want
                    elif not x.buy and want < x.sl - 0.01:
                        x.sl = want
            # ---- recovery
            self.manage_recovery(bid, ask, t)
        # ---- pendings
        if self.pend:
            shut = self.locked or self.is_holiday(t) or not self.in_window(t)
            for o in list(self.pend):
                if shut or t - o.t_setup >= max(1, P['limit_wait_bars']) * 300:
                    self.pend.remove(o)
        if newbar:
            self.new_bar(bid, ask, t, k)

    def manage_recovery(self, bid, ask, t):
        P = self.p
        if P['recover_at_atr'] <= 0:
            return
        ids = {x.id for x in self.pos}
        for x in list(self.pos):
            if x.tag == 'R' and x.parent not in ids:
                self.close_pos(x, bid if x.buy else ask, t, 'orphan')
        if self.locked:
            return
        if P['recover_hours_only'] and not self.in_window(t):
            return
        if P['recover_spike_guard'] and self.k_loaded > 0 and self.spike_now(self.k_loaded):
            return
        for x in list(self.pos):
            if x.tag in ('R', 'B1', 'L1'):
                continue
            if any(y.tag == 'R' and y.parent == x.id for y in self.pos):
                continue
            if x.sl <= 0 or (x.buy and x.sl >= x.op) or (not x.buy and x.sl <= x.op):
                continue
            a = x.atr_e
            adverse = (x.op - bid) if x.buy else (ask - x.op)
            if adverse < P['recover_at_atr'] * a:
                continue
            lot = max(0.01, min(math.floor(x.lots * P['recover_lot_mult'] / 0.01 + 1e-9) * 0.01, P['max_lot']))
            px = ask if x.buy else bid
            eq = self.equity(bid, ask)
            m = lot * P['contract'] * px / P['leverage']
            if m > (eq - self.used_margin(px)) * P['max_margin_pct'] / 100.0:
                continue
            avg = (x.op * x.lots + px * lot) / (x.lots + lot)
            tp = round(avg + P['recover_tp_atr'] * a if x.buy else avg - P['recover_tp_atr'] * a, 2)
            if x.buy and tp - bid <= 0:
                continue
            if not x.buy and ask - tp <= 0:
                continue
            gsl = x.sl
            if P['group_stop_atr'] > 0:
                c = round(px - P['group_stop_atr'] * a if x.buy else px + P['group_stop_atr'] * a, 2)
                if (x.buy and c > x.sl and bid - c > 0.01) or (not x.buy and c < x.sl and c - ask > 0.01):
                    gsl = c
            if P['max_open_risk_pct'] > 0:
                add = ((px - gsl) if x.buy else (gsl - px)) * lot * P['contract']
                if add > 0 and eq > 0 and self.open_risk_pct(bid, ask) + add / eq * 100 > P['max_open_risk_pct']:
                    continue
            self.open_pos('R', x.buy, lot, px, gsl, tp, t, a, parent=x.id)
            x.tp = tp
            x.sl = gsl

    def new_bar(self, bid, ask, t, k):
        P = self.p
        if k < 600:
            return
        self.k_loaded = k
        a = self.atr[k - 1]
        if not a > 0:
            return
        sig_t = int(self.b5['t'][k - 1])
        sh = dt.datetime.utcfromtimestamp(sig_t).hour
        if sh < P['start_hour'] or sh > P['end_hour']:
            return
        now = dt.datetime.utcfromtimestamp(t)
        if P['friday_filter'] and now.weekday() == 4 and now.hour >= P['friday_stop_hour']:
            return
        if self.locked or self.is_holiday(t):
            return
        h5, l5, c5 = self.b5['h'], self.b5['l'], self.b5['c']
        # ---- engine B
        if P['use_b1'] and sum(1 for x in self.pos if x.tag == 'B1') < P['b_max_pos']:
            cooled = (self.b5['t'][k] - self.last_break) >= P['b_cooldown'] * 300
            if cooled:
                avg = self.atr_avg50[k]
                d = 0
                bmin = c5[k - 1] * P['b_atr_min_pct'] / 100 if P['b_atr_min_pct'] > 0 else P['b_atr_min']
                if avg > 0 and a >= P['b_spike_min'] * avg and a >= bmin:
                    n = P['b_lookback']
                    hh = h5[k - 1 - n:k - 1].max()
                    ll = l5[k - 1 - n:k - 1].min()
                    if c5[k - 1] > hh:
                        d = 1
                    elif c5[k - 1] < ll:
                        d = -1
                if d != 0 and (ask - bid) <= P['max_spread_atr'] * a:
                    entry = ask if d == 1 else bid
                    sld = P['b_sl_atr'] * a
                    lot = self.calc_lot(entry, sld, bid, ask) * P['b_lot_mult']
                    lot = max(0.01, math.floor(lot / 0.01 + 1e-9) * 0.01)
                    sl = round(entry - sld if d == 1 else entry + sld, 2)
                    tp = round(entry + P['b_tp_atr'] * a if d == 1 else entry - P['b_tp_atr'] * a, 2)
                    self.open_pos('B1', d == 1, lot, entry, sl, tp, t, a)
                    self.last_break = self.b5['t'][k]
        # ---- position gate
        # ---- engine L
        if P['use_ldn']:
            self.check_london(bid, ask, t, k)
        orig = sum(1 for x in self.pos if x.tag not in ('R', 'B1', 'L1'))
        if orig + len(self.pend) >= P['max_positions']:
            return
        tr = self.trend(k)
        d, tag = 0, ''
        nospike = not self.spike_now(k)
        if P['use_s1'] and tr != 0 and nospike and not (P['adx_min'] > 0 and self.adx[k - 1] < P['adx_min']):
            if tr == 1 and l5[k - 1] <= self.bbl[k - 1]:
                d, tag = 1, 'S1'
            elif tr == -1 and h5[k - 1] >= self.bbu[k - 1]:
                d, tag = -1, 'S1'
        if d == 0 and P['use_s5'] and tr != 0:
            n = P['extreme_bars']
            top = max(self.spa[k - 1], self.spb[k - 1])
            bot = min(self.spa[k - 1], self.spb[k - 1])
            lo = l5[k - 1 - n:k - 1].min()
            hi = h5[k - 1 - n:k - 1].max()
            c1 = c5[k - 1]
            if tr == 1 and c1 <= lo and c1 > top:
                d, tag = 1, 'S5'
            elif tr == -1 and c1 >= hi and c1 < bot:
                d, tag = -1, 'S5'
        if d == 0:
            return
        if tag != 'S1' and P['adx_min'] > 0 and self.adx[k - 1] < P['adx_min']:
            return
        if not nospike:
            return
        # adaptive ATR floor
        n = P['atr_lookback']
        hist = self.atr[k - n:k]          # bars 1..n
        rank = 100.0 * np.count_nonzero(hist < a) / n
        hard = c5[k - 1] * P['atr_hard_min_pct'] / 100 if P['atr_hard_min_pct'] > 0 else P['atr_hard_min']
        if rank < P['atr_pctile'] or a < hard:
            return
        if P['range_bars'] > 0:
            n = P['range_bars'] + 1
            rng = (h5[k - n:k].max() - l5[k - n:k].min()) / a
            if rng < P['range_min_atr']:
                return
        self.open_trade(d, tag, bid, ask, t, a)

    def check_london(self, bid, ask, t, k):
        P = self.p
        b1 = int(self.b5['t'][k - 1])
        day0 = b1 - b1 % 86400
        if self.ldn_day == day0:
            return
        h = (b1 % 86400) // 3600
        if h < P['ldn_end'] or h >= P['ldn_close'] - 2:
            return
        hi, lo = -1e18, 1e18
        sh = k - 1
        while sh >= 0 and self.b5['t'][sh] >= day0:
            hh = (int(self.b5['t'][sh]) % 86400) // 3600
            if P['ldn_start'] <= hh < P['ldn_end']:
                hi = max(hi, self.b5['h'][sh]); lo = min(lo, self.b5['l'][sh])
            sh -= 1
        if not hi > lo:
            return
        c1 = self.b5['c'][k - 1]
        d = 1 if c1 > hi else -1 if c1 < lo else 0
        if d == 0:
            return
        self.ldn_day = day0
        if any(x.tag == 'L1' for x in self.pos):
            return
        entry = ask if d == 1 else bid
        rng = max(hi - lo, 0.5)
        lot = self.calc_lot(entry, rng, bid, ask) * P['ldn_lot_mult']
        lot = max(0.01, math.floor(lot / 0.01 + 1e-9) * 0.01)
        self.open_pos('L1', d == 1, lot, entry, round(entry - d * rng, 2), round(entry + d * P['ldn_tp'] * rng, 2), t, rng)

    def open_trade(self, d, tag, bid, ask, t, a):
        P = self.p
        spread = ask - bid
        if spread > a * P['max_spread_atr']:
            return
        sld = max(a * P['sl_atr'], spread + 0.01)
        tpd = max(a * P['tp_atr'], spread + 0.01)
        px = round(bid - P['limit_atr'] * a if d == 1 else ask + P['limit_atr'] * a, 2)
        sl = round(px - sld if d == 1 else px + sld, 2)
        tp = round(px + tpd if d == 1 else px - tpd, 2)
        lot = self.calc_lot(px, sld, bid, ask)
        if lot <= 0:
            return
        if P['max_open_risk_pct'] > 0:
            eq = self.equity(bid, ask)
            add = sld * lot * P['contract']
            if eq > 0 and self.open_risk_pct(bid, ask) + add / eq * 100 > P['max_open_risk_pct']:
                return
        self.nid += 1
        self.pend.append(Pend(self.nid, tag, d == 1, lot, px, sl, tp, t))


def summary(trades, deposit=5000.0, eq_curve=None):
    net = sum(x.net for x in trades)
    gw = sum(x.net for x in trades if x.net > 0)
    gl = -sum(x.net for x in trades if x.net < 0)
    bal = deposit
    pk = deposit
    dd = 0.0
    for x in sorted(trades, key=lambda x: x.t_close):
        bal += x.net
        pk = max(pk, bal)
        dd = max(dd, (pk - bal) / pk)
    return dict(n=len(trades), net=round(net), pf=round(gw / gl, 2) if gl else 99, dd_pct=round(dd * 100, 2),
                days=len({x.t_open // 86400 for x in trades}))
