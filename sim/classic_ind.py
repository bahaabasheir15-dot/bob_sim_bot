#!/usr/bin/env python3
"""Classic indicator strategies from short videos, tested on gold: RSI 30/70 reversal and Ichimoku cloud.
Signal at the close of a `tf`-minute bar, market entry at the next M1 open, ATR(14) stop / target,
one position at a time (sim.fast_scalp.run). Fixed 0.01 lot, P&L in $.
    python3 -m sim.classic_ind data/xauusd_plus_m1_2023_2026.npz
"""
import sys
import numpy as np
from . import indicators as ind
from .data import load_npz, resample
from .fast_scalp import run, stats


def _place(m, b, s, a, tp_atr, sl_atr):
    sig = np.zeros(len(m['t']), np.int8); tp = np.zeros(len(m['t'])); sl = np.zeros(len(m['t']))
    for k in np.flatnonzero(s):
        if a[k] > 0:
            j = b['last'][k]; sig[j] = s[k]; tp[j] = tp_atr * a[k]; sl[j] = sl_atr * a[k]
    return sig, tp, sl


def rsi_sig(m, tf, lo=30, hi=70, side=0):
    b = resample(m, tf); c = b['c']; r = ind.rsi(c, 14); a = ind.atr(b['h'], b['l'], c, 14)
    s = np.zeros(len(c), np.int8)
    s[1:][(r[:-1] < lo) & (r[1:] >= lo)] = 1          # RSI back up through 30 -> buy
    s[1:][(r[:-1] > hi) & (r[1:] <= hi)] = -1         # RSI back down through 70 -> sell
    if side:
        s[s != side] = 0
    return b, s, a


def ichi_sig(m, tf, side=0):
    b = resample(m, tf); h, l, c = b['h'], b['l'], b['c']; a = ind.atr(h, l, c, 14)
    mid = lambda n: (ind.rolling_max(h, n) + ind.rolling_min(l, n)) / 2
    ten, kij = mid(9), mid(26)
    sa = np.r_[np.full(26, np.nan), ((ten + kij) / 2)[:-26]]
    sb = np.r_[np.full(26, np.nan), mid(52)[:-26]]
    top, bot = np.fmax(sa, sb), np.fmin(sa, sb)
    s = np.zeros(len(c), np.int8)
    up = (ten > kij) & (np.r_[False, ten[:-1] <= kij[:-1]])
    dn = (ten < kij) & (np.r_[False, ten[:-1] >= kij[:-1]])
    s[up & (c > top)] = 1                               # tenkan crosses above kijun, price above the cloud
    s[dn & (c < bot)] = -1
    if side:
        s[s != side] = 0
    return b, s, a


def main(path):
    m = load_npz(path)
    for name, fn in (('RSI 30/70', rsi_sig), ('Ichimoku', ichi_sig)):
        for tf, hold in ((1440, 30), (240, 60), (60, 120)):
            for tpa, sla in ((2.0, 2.0), (3.0, 1.5), (4.0, 2.0)):
                b, s, a = fn(m, tf)
                sig, tp, sl = _place(m, b, s, a, tpa, sla)
                stats(run(m, sig, tp, sl, hold * tf, entry_gap=4 * 86400, close_gap=10 ** 9), f'{name} {"D1" if tf == 1440 else "H%d" % (tf // 60)} tp{tpa:g}/sl{sla:g}')
            for side, sn in ((1, 'BUY only'), (-1, 'SELL only')):
                b, s, a = fn(m, tf, side=side)
                sig, tp, sl = _place(m, b, s, a, 3.0, 1.5)
                stats(run(m, sig, tp, sl, hold * tf, entry_gap=4 * 86400, close_gap=10 ** 9), f'{name} {"D1" if tf == 1440 else "H%d" % (tf // 60)} {sn}')


if __name__ == '__main__':
    main(sys.argv[1])
