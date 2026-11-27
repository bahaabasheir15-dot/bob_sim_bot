#!/usr/bin/env python3
"""SMC model: change of character (CHoCH) or break of structure (BOS) + order block (OB) retest.
Bullish (bearish = mirror), on bars of `tf` minutes:
  swing highs/lows = fractals with `piv` bars on each side (known only `piv` bars later);
  CHoCH up = structure was bearish (last swing high below the one before) and a bar CLOSES above the last
  swing high; BOS up = structure bullish (higher high) and the same break. mode picks 'choch', 'bos' or 'both'.
  OB = the last bearish candle (close < open) between the lowest low before the break and the break bar.
  Entry: within `life` bars, a bar trades into the OB (low <= OB high) and closes above the OB low -> buy at the
  next open. Stop = OB low - 0.2 ATR. Target = `rr` x risk, or (rr=0) the highest high since the break
  (liquidity), only if that gives >= 1R. One trade per OB.
    python3 -m sim.smc_ob data/xauusd_plus_m1_2023_2026.npz
"""
import sys
import numpy as np
from . import indicators as ind
from .data import load_npz, resample
from .fast_scalp import run, stats


def signals(m, tf=15, piv=3, mode='choch', rr=2.0, life=40):
    b = resample(m, tf); o, h, l, c = b['o'], b['h'], b['l'], b['c']
    a = ind.atr(h, l, c, 14); n = len(c)
    sig = np.zeros(len(m['t']), np.int8); tp = np.zeros(len(m['t'])); sl = np.zeros(len(m['t']))
    sh, slw = [], []            # confirmed swings: (bar, price)
    used_h = used_l = -1        # swing already broken
    obs = []                    # [dir, bot, top, born, extreme]
    for k in range(2 * piv + 30, n - 1):
        p = k - piv             # pivot candidate becomes known now
        if h[p] == h[p - piv:p + piv + 1].max():
            sh.append((p, h[p]))
        if l[p] == l[p - piv:p + piv + 1].min():
            slw.append((p, l[p]))
        if not a[k] > 0:
            continue
        # manage live order blocks
        keep = []
        for z in obs:
            d, bot, top, born, ext = z
            if k - born > life:
                continue
            if d == 1:
                ext = max(ext, h[k])
                if c[k] < bot:
                    continue
                if l[k] <= top and k > born:
                    risk = c[k] - (bot - 0.2 * a[k])
                    tgt = rr * risk if rr > 0 else ext - c[k]
                    if 0.3 * a[k] <= risk <= 5 * a[k] and tgt >= risk:
                        j = b['last'][k]; sig[j] = 1; sl[j] = risk; tp[j] = tgt
                    continue
            else:
                ext = min(ext, l[k])
                if c[k] > top:
                    continue
                if h[k] >= bot and k > born:
                    risk = (top + 0.2 * a[k]) - c[k]
                    tgt = rr * risk if rr > 0 else c[k] - ext
                    if 0.3 * a[k] <= risk <= 5 * a[k] and tgt >= risk:
                        j = b['last'][k]; sig[j] = -1; sl[j] = risk; tp[j] = tgt
                    continue
            keep.append([d, bot, top, born, ext])
        obs = keep
        # structure breaks
        if len(sh) >= 2 and sh[-1][0] != used_h and c[k] > sh[-1][1]:
            bearish = sh[-1][1] < sh[-2][1]
            if mode == 'both' or (mode == 'choch') == bearish:
                i0 = sh[-1][0]
                lo_i = i0 + int(np.argmin(l[i0:k + 1]))
                cand = [i for i in range(lo_i, k + 1) if c[i] < o[i]]
                if cand:
                    i = cand[-1]; obs.append([1, l[i], h[i], k, h[k]])
            used_h = sh[-1][0]
        if len(slw) >= 2 and slw[-1][0] != used_l and c[k] < slw[-1][1]:
            bullish = slw[-1][1] > slw[-2][1]
            if mode == 'both' or (mode == 'choch') == bullish:
                i0 = slw[-1][0]
                hi_i = i0 + int(np.argmax(h[i0:k + 1]))
                cand = [i for i in range(hi_i, k + 1) if c[i] > o[i]]
                if cand:
                    i = cand[-1]; obs.append([-1, l[i], h[i], k, l[k]])
            used_l = slw[-1][0]
    return sig, tp, sl


def main(path):
    m = load_npz(path)
    for tf, hold in ((5, 288), (15, 192), (60, 72)):
        for mode in ('choch', 'bos'):
            for rr in (2.0, 3.0, 0.0):
                sig, tp, sl = signals(m, tf=tf, mode=mode, rr=rr)
                stats(run(m, sig, tp, sl, hold * tf, entry_gap=4 * 86400, close_gap=10 ** 9),
                      f'M{tf} {mode.upper()}+OB ' + (f'rr{rr:g}' if rr else 'TP=liquidity'))


if __name__ == '__main__':
    main(sys.argv[1])
