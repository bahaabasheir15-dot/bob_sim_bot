"""Candidate extra engines, tested on the same M1 bid/ask data at a fixed 0.01 lot.

Each engine decides on CLOSED bars of its own timeframe, enters at the next
minute's open (ask for buys, bid for sells), and is managed minute by minute on
the M1 path (worst case inside a minute: the stop is checked before the target).
Every trade costs the spread and $6 per lot round-trip commission.
"""
import datetime as dt

import numpy as np

from . import indicators as ind
from .data import resample

COMM = 0.06   # $ per 0.01 lot round trip


def _hour(t):
    return (t // 3600) % 24


def _dow(t):
    return dt.datetime.utcfromtimestamp(int(t)).weekday()


def run_engine(m1, tf_min, signal_fn, manage, max_open=1, name='C'):
    """signal_fn(bars, i) -> +1/-1/0 decided on closed bar i.
    manage: dict(sl=price_dist_fn(bars,i), trail=dist_fn or None, tp=dist_fn or None, max_bars=int or None,
                 exit_fn=fn(bars,i,dir)->bool on each closed bar)"""
    b = resample(m1, tf_min)
    t1 = m1['t']
    # first M1 index of each bar
    first = b['first']
    trades = []
    open_ = []
    nb = len(b['t'])
    for i in range(60, nb - 1):
        # manage open positions inside bar i+1 minute by minute
        d = signal_fn(b, i)
        if d != 0 and len(open_) < max_open:
            j = first[i + 1]
            entry = m1['ao'][j] if d == 1 else m1['bo'][j]
            sl_d = manage['sl'](b, i)
            tp_d = manage['tp'](b, i) if manage.get('tp') else None
            open_.append(dict(d=d, op=entry, sl=entry - d * sl_d, tp=(entry + d * tp_d) if tp_d else None,
                              t=int(t1[j]), i0=i + 1, best=entry, name=name))
        j0, j1 = first[i + 1], (first[i + 2] if i + 2 < nb else len(t1))
        for j in range(j0, j1):
            if not open_:
                break
            for p in list(open_):
                if p['t'] > t1[j]:
                    continue
                d = p['d']
                lo = m1['bl'][j] if d == 1 else m1['al'][j]
                hi = m1['bh'][j] if d == 1 else m1['ah'][j]
                adverse = lo if d == 1 else hi
                fav = hi if d == 1 else lo
                if (d == 1 and adverse <= p['sl']) or (d == -1 and adverse >= p['sl']):
                    _close(p, p['sl'], t1[j], 'sl', trades, open_)
                    continue
                if p['tp'] is not None and ((d == 1 and fav >= p['tp']) or (d == -1 and fav <= p['tp'])):
                    _close(p, p['tp'], t1[j], 'tp', trades, open_)
                    continue
                if manage.get('trail'):
                    p['best'] = max(p['best'], fav) if d == 1 else min(p['best'], fav)
        # end of bar i+1: trailing update, time/exit rules on the closed bar
        for p in list(open_):
            d = p['d']
            if manage.get('trail'):
                td = manage['trail'](b, i + 1)
                ns = p['best'] - d * td
                if (d == 1 and ns > p['sl']) or (d == -1 and ns < p['sl']):
                    p['sl'] = ns
            age = i + 1 - p['i0']
            ex = manage.get('max_bars') and age >= manage['max_bars']
            if not ex and manage.get('exit_fn'):
                ex = manage['exit_fn'](b, i + 1, d)
            if ex:
                j = min(j1, len(t1) - 1)
                px = m1['bo'][j] if d == 1 else m1['ao'][j]
                _close(p, px, t1[j], 'exit', trades, open_)
    return trades


def _close(p, px, t, why, trades, open_):
    g = (px - p['op']) * p['d']           # $ per 1 oz = per 0.01 lot
    trades.append(dict(name=p['name'], d=p['d'], t_open=p['t'], t_close=int(t), op=p['op'], cp=px,
                       net=g - COMM, why=why))
    open_.remove(p)


# ---------------------------------------------------------------- engines
def donchian(m1, tf=60, n=20, sl_atr=2.0, trail_atr=3.0):
    b = resample(m1, tf)
    a = ind.atr(b['h'], b['l'], b['c'], 14)
    hh = ind.rolling_max(b['h'], n)
    ll = ind.rolling_min(b['l'], n)

    def sig(bb, i):
        if np.isnan(hh[i - 1]):
            return 0
        if bb['c'][i] > hh[i - 1]:
            return 1
        if bb['c'][i] < ll[i - 1]:
            return -1
        return 0
    return run_engine(m1, tf, sig, dict(sl=lambda bb, i: sl_atr * a[i], trail=lambda bb, i: trail_atr * a[i]),
                      name=f'DON{tf}/{n}')


def london_breakout(m1, start_h=3, end_h=9, close_h=21, tp_mult=1.0):
    """Range of server hours [start_h, end_h); trade the first M5 close outside it, stop at the other side."""
    b = resample(m1, 5)
    t = b['t']
    day = t // 86400
    h = _hour(t)
    rng_hi = {}
    rng_lo = {}
    for i in range(len(t)):
        if start_h <= h[i] < end_h:
            dd = day[i]
            rng_hi[dd] = max(rng_hi.get(dd, -1e9), b['h'][i])
            rng_lo[dd] = min(rng_lo.get(dd, 1e9), b['l'][i])
    done = set()

    def sig(bb, i):
        dd = day[i]
        if dd in done or not (end_h <= h[i] < close_h - 2) or dd not in rng_hi:
            return 0
        if bb['c'][i] > rng_hi[dd]:
            done.add(dd); return 1
        if bb['c'][i] < rng_lo[dd]:
            done.add(dd); return -1
        return 0

    def sl(bb, i):
        return max(rng_hi[day[i]] - rng_lo[day[i]], 0.5)

    def ex(bb, i, d):
        return h[i] >= close_h

    return run_engine(m1, 5, sig, dict(sl=sl, tp=lambda bb, i: tp_mult * sl(bb, i), exit_fn=ex), name='LDN')


def rsi2_pullback(m1, tf=60, lo=10, hi=90, trend=200):
    """Connors-style: in the direction of the long average, buy an RSI(2) dip, exit on close above SMA(5)."""
    b = resample(m1, tf)
    c = b['c']
    d_ = np.diff(c, prepend=c[0])
    up = ind.ema(np.maximum(d_, 0), 3)      # RSI(2) via Wilder ~ EMA(2n-1)
    dn = ind.ema(np.maximum(-d_, 0), 3)
    rsi = 100 - 100 / (1 + up / np.where(dn == 0, 1e-9, dn))
    sma_t = ind.sma(c, trend)
    sma5 = ind.sma(c, 5)
    a = ind.atr(b['h'], b['l'], c, 14)

    def sig(bb, i):
        if np.isnan(sma_t[i]):
            return 0
        if c[i] > sma_t[i] and rsi[i] < lo:
            return 1
        if c[i] < sma_t[i] and rsi[i] > hi:
            return -1
        return 0

    def ex(bb, i, d):
        return (d == 1 and c[i] > sma5[i]) or (d == -1 and c[i] < sma5[i])

    return run_engine(m1, tf, sig, dict(sl=lambda bb, i: 3 * a[i], exit_fn=ex, max_bars=24), name=f'RSI2-{tf}')


def session_breakout(m1, start_h, end_h, trade_until_h, close_h, tp_mult=1.0, name='SES', fade=False):
    """Generic version of london_breakout: range of server hours [start_h, end_h), first M5 close
    outside it between end_h and trade_until_h is traded (or faded), stop = one range width,
    target = tp_mult range widths, flat at close_h."""
    b = resample(m1, 5)
    t = b['t']
    day = t // 86400
    h = _hour(t)
    rng_hi, rng_lo = {}, {}
    for i in range(len(t)):
        if start_h <= h[i] < end_h:
            dd = day[i]
            rng_hi[dd] = max(rng_hi.get(dd, -1e9), b['h'][i])
            rng_lo[dd] = min(rng_lo.get(dd, 1e9), b['l'][i])
    done = set()

    def sig(bb, i):
        dd = day[i]
        if dd in done or not (end_h <= h[i] < trade_until_h) or dd not in rng_hi:
            return 0
        d = 1 if bb['c'][i] > rng_hi[dd] else -1 if bb['c'][i] < rng_lo[dd] else 0
        if d:
            done.add(dd)
        return -d if fade else d

    def sl(bb, i):
        return max(rng_hi[day[i]] - rng_lo[day[i]], 0.5)

    return run_engine(m1, 5, sig, dict(sl=sl, tp=lambda bb, i: tp_mult * sl(bb, i),
                                        exit_fn=lambda bb, i, d: h[i] >= close_h or day[i] != day[i - 1]), name=name)


def prev_day_breakout(m1, trade_from=9, close_h=21, tp_mult=1.0, name='PDB'):
    """Break of yesterday's high / low (server days), stop = half of yesterday's range."""
    b = resample(m1, 5)
    t = b['t']
    day = t // 86400
    h = _hour(t)
    dh, dl = {}, {}
    for i in range(len(t)):
        dh[day[i]] = max(dh.get(day[i], -1e9), b['h'][i])
        dl[day[i]] = min(dl.get(day[i], 1e9), b['l'][i])
    days = sorted(dh)
    prev = {days[k]: days[k - 1] for k in range(1, len(days))}
    done = set()

    def sig(bb, i):
        dd = day[i]
        if dd in done or dd not in prev or not (trade_from <= h[i] < close_h - 2):
            return 0
        p = prev[dd]
        if bb['c'][i] > dh[p]:
            done.add(dd); return 1
        if bb['c'][i] < dl[p]:
            done.add(dd); return -1
        return 0

    def sl(bb, i):
        p = prev[day[i]]
        return max((dh[p] - dl[p]) * 0.5, 0.5)

    return run_engine(m1, 5, sig, dict(sl=sl, tp=lambda bb, i: tp_mult * sl(bb, i),
                                        exit_fn=lambda bb, i, d: h[i] >= close_h or day[i] != day[i - 1]), name=name)


def momentum_pullback_h1(m1, rsi_lo=55, rsi_hi=80, dmin=0.5, dmax=3.0, need_pullback=True,
                         sl_d=40.0, tp_d=25.0, trail_from=16.0, trail_d=16.0, pct=False,
                         skip=(11, 15), max_open=2, name='MPB'):
    """Engine modelled on the MyAiGold trade log: decide on the closed H1 candle, enter at the next
    H1 open in the direction of a rising/falling EMA20 when RSI is strong but not extreme, the
    close is 0.5-3 ATR from the EMA, and the last candle pulled back. Exits: fixed stop / target,
    and a stop that trails `trail_d` behind the best price once the trade is `trail_from` in profit,
    checked every minute. pct=True turns the dollar distances into % of price (x/4400)."""
    b = resample(m1, 60)
    c, h, l, o = b['c'], b['h'], b['l'], b['o']
    e20 = ind.ema(c, 20)
    r = ind.rsi(c, 14)
    a = ind.atr(h, l, c, 14)
    hr = (b['t'] % 86400) // 3600
    t1 = m1['t']
    first = b['first']
    trades, open_ = [], []
    for i in range(250, len(c) - 1):
        k = i + 1                                   # the bar that opens now
        if not (skip[0] <= hr[k] < skip[1]) and len(open_) < max_open:
            for d in (1, -1):
                rr = r[i] if d == 1 else 100 - r[i]
                dist = d * (c[i] - e20[i]) / a[i] if a[i] > 0 else 0
                ok = (d * (c[i] - e20[i]) > 0 and d * (e20[i] - e20[i - 3]) > 0 and rsi_lo <= rr < rsi_hi
                      and dmin <= dist < dmax and (not need_pullback or d * (c[i] - o[i]) < 0))
                if ok and not any(p['d'] == d for p in open_):
                    j = first[k]
                    entry = m1['ao'][j] if d == 1 else m1['bo'][j]
                    sc = entry / 4400.0 if pct else 1.0
                    open_.append(dict(d=d, op=entry, sl=entry - d * sl_d * sc, tp=entry + d * tp_d * sc,
                                      best=entry, t=int(t1[j]), sc=sc, name=name))
                    break
        j0, j1 = first[k], (first[k + 1] if k + 1 < len(c) else len(t1))
        for j in range(j0, j1):
            if not open_:
                break
            for p in list(open_):
                d = p['d']
                if d == 1:
                    path = (m1['bl'][j], m1['bh'][j]) if m1['bc'][j] >= m1['bo'][j] else (m1['bh'][j], m1['bl'][j])
                else:
                    path = (m1['al'][j], m1['ah'][j]) if m1['ac'][j] >= m1['ao'][j] else (m1['ah'][j], m1['al'][j])
                done = False
                for px in path:
                    if (d == 1 and px <= p['sl']) or (d == -1 and px >= p['sl']):
                        _close(p, p['sl'], t1[j], 'sl', trades, open_); done = True; break
                    if (d == 1 and px >= p['tp']) or (d == -1 and px <= p['tp']):
                        _close(p, p['tp'], t1[j], 'tp', trades, open_); done = True; break
                    p['best'] = max(p['best'], px) if d == 1 else min(p['best'], px)
                    if d * (p['best'] - p['op']) >= trail_from * p['sc']:
                        ns = p['best'] - d * trail_d * p['sc']
                        if (d == 1 and ns > p['sl']) or (d == -1 and ns < p['sl']):
                            p['sl'] = ns
                if done:
                    continue
    return trades


def liquidity_sweep(m1, start_h=3, end_h=9, until_h=18, close_h=21, rr=2.0, buf=0.1, name='SWP',
                    level='asia'):
    """ICT-style liquidity grab. level='asia': the Asian range high/low; level='pdhl': yesterday's
    high/low. After end_h, price trades BEYOND the level (stops taken) and then an M5 candle closes
    back inside -> enter the other way. Stop just beyond the sweep extreme (+buf x range), target
    rr x the risk, flat at close_h. One trade a day."""
    b = resample(m1, 5)
    t = b['t']
    day = t // 86400
    h = _hour(t)
    hi_l, lo_l = {}, {}
    if level == 'asia':
        for i in range(len(t)):
            if start_h <= h[i] < end_h:
                dd = day[i]
                hi_l[dd] = max(hi_l.get(dd, -1e9), b['h'][i])
                lo_l[dd] = min(lo_l.get(dd, 1e9), b['l'][i])
    else:
        dh, dl = {}, {}
        for i in range(len(t)):
            dh[day[i]] = max(dh.get(day[i], -1e9), b['h'][i])
            dl[day[i]] = min(dl.get(day[i], 1e9), b['l'][i])
        ds = sorted(dh)
        for k in range(1, len(ds)):
            hi_l[ds[k]] = dh[ds[k - 1]]
            lo_l[ds[k]] = dl[ds[k - 1]]
    st = {}       # per day: extreme beyond the level so far
    done = set()
    sl_dist = {}

    def sig(bb, i):
        dd = day[i]
        if dd in done or dd not in hi_l or not (end_h <= h[i] < until_h):
            return 0
        H, L = hi_l[dd], lo_l[dd]
        rng = max(H - L, 0.5)
        s = st.setdefault(dd, {'up': None, 'dn': None})
        if bb['h'][i] > H:
            s['up'] = max(s['up'] or -1e9, bb['h'][i])
        if bb['l'][i] < L:
            s['dn'] = min(s['dn'] or 1e9, bb['l'][i])
        c = bb['c'][i]
        if s['up'] is not None and c < H and c > L:
            done.add(dd)
            sl_dist[i] = (s['up'] - c) + buf * rng
            return -1
        if s['dn'] is not None and c > L and c < H:
            done.add(dd)
            sl_dist[i] = (c - s['dn']) + buf * rng
            return 1
        return 0

    return run_engine(m1, 5, sig, dict(sl=lambda bb, i: max(sl_dist[i], 0.5),
                                        tp=lambda bb, i: rr * max(sl_dist[i], 0.5),
                                        exit_fn=lambda bb, i, d: h[i] >= close_h or day[i] != day[i - 1]), name=name)


def vwap_engine(m1, vol, mode='trend', anchor_h=0, from_h=9, until_h=19, close_h=21,
                touch=0.0, slope_k=0.1, sl_sd=1.5, rr=1.5, flat_k=0.05, ext_sd=2.0, name='VWAP'):
    """Session VWAP (anchored at server hour `anchor_h`) with volume-weighted +-sd bands, M5.
    mode 'trend': VWAP rising (falling) by more than slope_k x ATR over the last hour; the closed
        candle dipped to VWAP + touch x sd (touch=0: VWAP itself, -1: the -1 sd band) and closed back
        above VWAP -> buy (mirror for sell). Stop sl_sd x sd below VWAP, target rr x risk.
    mode 'range': VWAP flat (|slope| < flat_k x ATR); close beyond +-ext_sd x sd -> fade back to VWAP,
        stop at +-(ext_sd + 1) sd.  One trade per day, flat at close_h."""
    b = resample(m1, 5)
    v = np.add.reduceat(vol.astype(np.float64), b['first'])
    t = b['t']
    tp = (b['h'] + b['l'] + b['c']) / 3.0
    sess = (t - anchor_h * 3600) // 86400
    cv = np.zeros(len(t)); cpv = np.zeros(len(t)); cp2 = np.zeros(len(t))
    for i in range(len(t)):
        if i == 0 or sess[i] != sess[i - 1]:
            cv[i], cpv[i], cp2[i] = v[i], v[i] * tp[i], v[i] * tp[i] ** 2
        else:
            cv[i], cpv[i], cp2[i] = cv[i - 1] + v[i], cpv[i - 1] + v[i] * tp[i], cp2[i - 1] + v[i] * tp[i] ** 2
    vw = cpv / np.maximum(cv, 1e-9)
    sd = np.sqrt(np.maximum(cp2 / np.maximum(cv, 1e-9) - vw ** 2, 0.0))
    a = ind.atr(b['h'], b['l'], b['c'], 14)
    h = _hour(t)
    day = t // 86400
    done = set()
    dist = {}

    def sig(bb, i):
        if i < 13 or day[i] in done or not (from_h <= h[i] < until_h) or sess[i] != sess[i - 12]:
            return 0
        if not (a[i] > 0 and sd[i] > 0):
            return 0
        slope = vw[i] - vw[i - 12]
        c = bb['c'][i]
        if mode == 'trend':
            if slope > slope_k * a[i] and bb['l'][i] <= vw[i] + touch * sd[i] and c > vw[i]:
                done.add(day[i]); dist[i] = (c - (vw[i] - sl_sd * sd[i]), None); return 1
            if slope < -slope_k * a[i] and bb['h'][i] >= vw[i] - touch * sd[i] and c < vw[i]:
                done.add(day[i]); dist[i] = ((vw[i] + sl_sd * sd[i]) - c, None); return -1
        else:
            if abs(slope) < flat_k * a[i]:
                if c >= vw[i] + ext_sd * sd[i]:
                    done.add(day[i]); dist[i] = (vw[i] + (ext_sd + 1) * sd[i] - c, c - vw[i]); return -1
                if c <= vw[i] - ext_sd * sd[i]:
                    done.add(day[i]); dist[i] = (c - (vw[i] - (ext_sd + 1) * sd[i]), vw[i] - c); return 1
        return 0

    def sl(bb, i):
        return max(dist[i][0], 0.5)

    def tpf(bb, i):
        r, target = dist[i]
        return max(target, 0.3) if target is not None else rr * max(r, 0.5)

    return run_engine(m1, 5, sig, dict(sl=sl, tp=tpf, exit_fn=lambda bb, i, d: h[i] >= close_h or day[i] != day[i - 1]),
                      name=name)
