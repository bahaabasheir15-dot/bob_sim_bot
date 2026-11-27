#!/usr/bin/env python3
"""'Simple strategy' from a YouTube short (@snip_trader): trend + MA21 + broken level + retest.

Sell rules (buy = mirror), on bars of `tf` minutes:
 1. downtrend: close < EMA21 and EMA21 falling (below its value `slope_n` bars ago);
 2. a support level = lowest low of the previous `look` bars; price CLOSES below it (breakdown);
 3. within `wait` bars after the breakdown price comes back up to the level (high >= level - zone)
    and the bar closes back below the level and below EMA21 (rejected retest) -> sell at next open;
    optional: EMA21 is within `ma_near` ATR of the level (the MA and the level meet, as in the video);
 4. stop above the retest high (+0.2 ATR), target = `rr` x risk; one trade per level; time stop `hold_bars`.
    python3 -m sim.ma_retest data/xauusd_plus_m1_2023_2026.npz
"""
import sys
import numpy as np
from . import indicators as ind
from .data import load_npz, resample
from .fast_scalp import run, stats


def signals(m, tf=60, look=20, wait=20, zone=0.3, rr=3.0, slope_n=3, ma_near=0.0, min_risk_atr=0.5, max_risk_atr=3.0):
    b = resample(m, tf)
    o, h, l, c = b['o'], b['h'], b['l'], b['c']
    e = ind.ema(c, 21)
    a = ind.atr(h, l, c, 14)
    n = len(c)
    sig = np.zeros(len(m['t']), np.int8); tp = np.zeros(len(m['t'])); sl = np.zeros(len(m['t']))
    lv = {1: None, -1: None}           # active broken level per direction: (level, bar of break, extreme since)
    for k in range(max(look, 30) + 1, n - 1):
        if not a[k] > 0:
            continue
        for d in (-1, 1):
            # 1) new breakdown (d=-1: close below the lowest low of the last `look` bars) / breakout (d=+1)
            ref = l[k - look:k].min() if d == -1 else h[k - look:k].max()
            if (d == -1 and c[k] < ref) or (d == 1 and c[k] > ref):
                lv[d] = [ref, k]
                continue
            L = lv[d]
            if L is None:
                continue
            ref, kb = L
            if k - kb > wait:
                lv[d] = None
                continue
            trend = (c[k] < e[k] and e[k] < e[k - slope_n]) if d == -1 else (c[k] > e[k] and e[k] > e[k - slope_n])
            if not trend:
                continue
            z = zone * a[k]
            touched = (h[k] >= ref - z and c[k] < ref) if d == -1 else (l[k] <= ref + z and c[k] > ref)
            if not touched:
                continue
            if ma_near > 0 and abs(e[k] - ref) > ma_near * a[k]:
                continue
            stop = (max(h[k], ref) + 0.2 * a[k]) if d == -1 else (min(l[k], ref) - 0.2 * a[k])
            risk = abs(stop - c[k])
            if not (min_risk_atr * a[k] <= risk <= max_risk_atr * a[k]):
                continue
            j = b['last'][k]
            sig[j] = d; sl[j] = risk; tp[j] = rr * risk
            lv[d] = None                    # one trade per level
    return sig, tp, sl


def main(path):
    m = load_npz(path)
    for tf, hold in ((15, 96), (60, 72), (240, 30)):
        for rr in (2.0, 3.0):
            for near in (0.0, 1.0):
                sig, tp, sl = signals(m, tf=tf, rr=rr, ma_near=near)
                stats(run(m, sig, tp, sl, hold * tf), f'M{tf} rr{rr:.0f} MAnear{near:.0f}')


if __name__ == '__main__':
    main(sys.argv[1])
