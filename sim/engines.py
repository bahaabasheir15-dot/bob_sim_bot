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
