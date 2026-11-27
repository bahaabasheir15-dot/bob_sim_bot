#!/usr/bin/env python3
"""'Fake rejection at support' (short video): a strong down run (`run` bearish candles in a row, lower highs),
then a candle with a long lower wick at the bottom (looks like a hammer at support), then within `wait` bars a
small bounce candle (green) that stays below the hammer's high -> SELL at its close, expecting the support to
break. Stop above the highest high of hammer..bounce + 0.2 ATR, target `rr` x risk. Buy = mirror (top trap).
`fade=True` does the opposite (buy the hammer bounce) as a control.
    python3 -m sim.trap_break data/xauusd_plus_m1_2023_2026.npz
"""
import sys
import numpy as np
from . import indicators as ind
from .data import load_npz, resample
from .fast_scalp import run, stats


def signals(m, tf=15, run_n=4, wick=1.5, wait=3, rr=2.0, fade=False):
    b = resample(m, tf); o, h, l, c = b['o'], b['h'], b['l'], b['c']
    a = ind.atr(h, l, c, 14); n = len(c)
    sig = np.zeros(len(m['t']), np.int8); tp = np.zeros(len(m['t'])); sl = np.zeros(len(m['t']))
    for k in range(run_n + 20, n):
        if not a[k] > 0:
            continue
        for d in (-1, 1):                                   # d = direction of the run (-1 down)
            for w in range(1, wait + 1):                    # hammer at k-w, bounce at k
                hk = k - w
                r0 = hk - run_n
                bars = range(r0, hk)
                if d == -1:
                    ok = all(c[i] < o[i] for i in bars) and all(h[i + 1] < h[i] for i in range(r0, hk - 1))
                    body = abs(c[hk] - o[hk]); lw = min(o[hk], c[hk]) - l[hk]
                    ok = ok and lw >= wick * max(body, 0.05) and l[hk] < l[hk - 1]
                    ok = ok and c[k] > o[k] and h[k] < h[hk] and all(l[i] > l[hk] for i in range(hk + 1, k + 1))
                    if ok:
                        top = h[hk:k + 1].max() + 0.2 * a[k]; risk = top - c[k]
                        if 0.2 * a[k] <= risk <= 4 * a[k]:
                            j = b['last'][k]; sig[j] = 1 if fade else -1
                            sl[j] = (c[k] - (l[hk] - 0.2 * a[k])) if fade else risk
                            tp[j] = rr * sl[j]
                        break
                else:
                    ok = all(c[i] > o[i] for i in bars) and all(l[i + 1] > l[i] for i in range(r0, hk - 1))
                    body = abs(c[hk] - o[hk]); uw = h[hk] - max(o[hk], c[hk])
                    ok = ok and uw >= wick * max(body, 0.05) and h[hk] > h[hk - 1]
                    ok = ok and c[k] < o[k] and l[k] > l[hk] and all(h[i] < h[hk] for i in range(hk + 1, k + 1))
                    if ok:
                        bot = l[hk:k + 1].min() - 0.2 * a[k]; risk = c[k] - bot
                        if 0.2 * a[k] <= risk <= 4 * a[k]:
                            j = b['last'][k]; sig[j] = -1 if fade else 1
                            sl[j] = ((h[hk] + 0.2 * a[k]) - c[k]) if fade else risk
                            tp[j] = rr * sl[j]
                        break
    return sig, tp, sl


def main(path):
    m = load_npz(path)
    for tf, hold in ((5, 288), (15, 192), (60, 72)):
        for run_n in (4, 5):
            for rr in (1.5, 2.0, 3.0):
                sig, tp, sl = signals(m, tf=tf, run_n=run_n, rr=rr)
                stats(run(m, sig, tp, sl, hold * tf, entry_gap=4 * 86400, close_gap=10 ** 9), f'M{tf} run{run_n} rr{rr:g} TRAP-continue')
        sig, tp, sl = signals(m, tf=tf, run_n=4, rr=2.0, fade=True)
        stats(run(m, sig, tp, sl, hold * tf, entry_gap=4 * 86400, close_gap=10 ** 9), f'M{tf} run4 rr2 (control: buy the hammer)')


if __name__ == '__main__':
    main(sys.argv[1])
