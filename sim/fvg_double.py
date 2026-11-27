#!/usr/bin/env python3
"""'DOUBLE FVG MITIGATION' model (short video): 1) a fair value gap, 2) in the discount (buy) / premium (sell)
half of the dealing range, 3) price already came back into it once, 4) enter on the SECOND visit after a
reaction candle. Buy = mirror of sell.
  bullish FVG at bar k: low[k] > high[k-2], zone [high[k-2], low[k]]; the zone must lie below the middle of the
  last `rng` bars' range (discount). Visit = a bar whose low enters the zone; the visit ends when a later bar's
  low is back above the zone. A close below the zone kills it. Second visit + bullish candle closing above the
  zone top -> buy at next open, stop below the zone bottom - 0.2 ATR, target `rr` x risk. Zone expires after
  `life` bars.
    python3 -m sim.fvg_double data/xauusd_plus_m1_2023_2026.npz
"""
import sys
import numpy as np
from . import indicators as ind
from .data import load_npz, resample
from .fast_scalp import run, stats


def signals(m, tf=15, rng=50, rr=2.0, life=100, min_gap_atr=0.3, visits=2, pd=True):
    b = resample(m, tf); o, h, l, c = b['o'], b['h'], b['l'], b['c']
    a = ind.atr(h, l, c, 14); n = len(c)
    sig = np.zeros(len(m['t']), np.int8); tp = np.zeros(len(m['t'])); sl = np.zeros(len(m['t']))
    zones = []      # [dir, bottom, top, born, visits, inside]
    for k in range(rng + 2, n - 1):
        if not a[k] > 0:
            continue
        # update zones with bar k
        keep = []
        fired = False
        for z in zones:
            d, bot, top, born, vis, inside = z
            if k - born > life:
                continue
            if d == 1:
                if c[k] < bot:
                    continue                          # filled through -> dead
                touch = l[k] <= top
                if touch and not inside:
                    vis += 1; inside = True
                    if vis == visits and c[k] > top and c[k] > o[k] and not fired:
                        risk = c[k] - (bot - 0.2 * a[k])
                        if 0.3 * a[k] <= risk <= 4 * a[k]:
                            j = b['last'][k]; sig[j] = 1; sl[j] = risk; tp[j] = rr * risk; fired = True
                        continue                      # used
                elif not touch:
                    inside = False
            else:
                if c[k] > top:
                    continue
                touch = h[k] >= bot
                if touch and not inside:
                    vis += 1; inside = True
                    if vis == visits and c[k] < bot and c[k] < o[k] and not fired:
                        risk = (top + 0.2 * a[k]) - c[k]
                        if 0.3 * a[k] <= risk <= 4 * a[k]:
                            j = b['last'][k]; sig[j] = -1; sl[j] = risk; tp[j] = rr * risk; fired = True
                        continue
                elif not touch:
                    inside = False
            keep.append([d, bot, top, born, vis, inside])
        zones = keep
        # new FVG formed by bars k-2, k-1, k
        hi, lo = h[k - rng:k + 1].max(), l[k - rng:k + 1].min(); mid = (hi + lo) / 2
        if l[k] > h[k - 2] and l[k] - h[k - 2] >= min_gap_atr * a[k]:
            if not pd or l[k] < mid:                  # bullish gap in discount
                zones.append([1, h[k - 2], l[k], k, 0, False])
        if h[k] < l[k - 2] and l[k - 2] - h[k] >= min_gap_atr * a[k]:
            if not pd or h[k] > mid:                  # bearish gap in premium
                zones.append([-1, h[k], l[k - 2], k, 0, False])
    return sig, tp, sl


def main(path):
    m = load_npz(path)
    for tf, hold in ((5, 288), (15, 192), (60, 72)):
        for rr in (2.0, 3.0):
            for vis, pd, tag in ((2, True, 'DOUBLE+PD'), (1, True, 'first visit+PD'), (2, False, 'DOUBLE no PD')):
                sig, tp, sl = signals(m, tf=tf, rr=rr, visits=vis, pd=pd)
                stats(run(m, sig, tp, sl, hold * tf, entry_gap=4 * 86400, close_gap=10 ** 9), f'M{tf} rr{rr:g} {tag}')


if __name__ == '__main__':
    main(sys.argv[1])
