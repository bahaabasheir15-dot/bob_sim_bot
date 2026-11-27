#!/usr/bin/env python3
"""Support / resistance + timing, designed and tested by Claude (user: "try it yourself").
LEVELS (H1): swing highs/lows = fractals with 3 bars per side. A level is STRONG when >= `touches` swing points
(highs and lows together, last `look` H1 bars, only swings already confirmed) lie within `tol` x ATR(H1) of
each other; its price = their average.
TIMING (`tf` bars, M15 default), in hours `h0`..`h1` server:
  BUY at a support: a strong level below the close; the bar's low reached it (low <= level + 0.25 ATR_H1) and the
  bar rejected it: lower wick >= `wick` x body, close in the upper half of the bar, close above the level.
  SELL at a resistance = mirror. Optional `trend`: only with the H4 EMA50 slope.
EXIT: stop = level -/+ `sl_atr` x ATR_H1; target = `rr` x risk, or (rr=0) the next strong level (>= 1R).
    python3 -m sim.sr_levels data/xauusd_plus_m1_2023_2026.npz
"""
import sys
import numpy as np
from . import indicators as ind
from .data import load_npz, resample
from .fast_scalp import run, stats


def h1_levels(m, piv=3, look=200, tol=0.3, touches=2):
    H = resample(m, 60); h, l, c = H['h'], H['l'], H['c']
    a = ind.atr(h, l, c, 14)
    pts_t, pts_p = [], []
    levels = [np.array([])] * len(c)
    for k in range(2 * piv + 1, len(c)):
        p = k - piv
        if h[p] == h[p - piv:p + piv + 1].max():
            pts_t.append(p); pts_p.append(h[p])
        if l[p] == l[p - piv:p + piv + 1].min():
            pts_t.append(p); pts_p.append(l[p])
        if not a[k] > 0:
            continue
        P = np.array([pp for tt, pp in zip(pts_t[-80:], pts_p[-80:]) if tt >= k - look])
        if len(P) < touches:
            continue
        D = np.abs(P[:, None] - P[None, :]) <= tol * a[k]
        cnt = D.sum(1)
        lv = []
        used = np.zeros(len(P), bool)
        for i in np.argsort(-cnt):
            if cnt[i] < touches or used[i]:
                continue
            grp = D[i] & ~used
            lv.append(P[grp].mean()); used |= D[i]
        levels[k] = np.array(sorted(lv))
    return H, a, levels


def signals(m, tf=15, rr=2.0, sl_atr=0.5, wick=1.5, h0=9, h1=21, trend=False, touches=2, tol=0.3):
    H, aH, LV = h1_levels(m, touches=touches, tol=tol)
    b = resample(m, tf); o, h, l, c, t = b['o'], b['h'], b['l'], b['c'], b['t']
    jh = np.searchsorted(H['t'], t, side='right') - 2          # last CLOSED H1 bar
    H4 = resample(m, 240); e4 = ind.ema(H4['c'], 50); j4 = np.searchsorted(H4['t'], t, side='right') - 2
    sig = np.zeros(len(m['t']), np.int8); tp = np.zeros(len(m['t'])); sl = np.zeros(len(m['t']))
    hr = (t % 86400) // 3600
    for k in range(len(c)):
        j = jh[k]
        if j < 10 or not (h0 <= hr[k] <= h1):
            continue
        lv = LV[j]; a = aH[j]
        if len(lv) == 0 or not a > 0:
            continue
        rng = h[k] - l[k]
        if rng <= 0:
            continue
        body = abs(c[k] - o[k]); lw = min(o[k], c[k]) - l[k]; uw = h[k] - max(o[k], c[k])
        up4 = e4[j4[k]] > e4[j4[k] - 3] if j4[k] > 3 else None
        # support
        below = lv[lv < c[k]]
        if len(below):
            L = below[-1]
            if l[k] <= L + 0.25 * a and lw >= wick * max(body, 0.05) and c[k] > l[k] + 0.5 * rng and (not trend or up4):
                risk = c[k] - (L - sl_atr * a)
                if rr > 0:
                    tgt = rr * risk
                else:
                    above = lv[lv > c[k] + risk]
                    tgt = (above[0] - c[k]) if len(above) else 0
                if risk > 0 and tgt >= risk:
                    jj = b['last'][k]; sig[jj] = 1; sl[jj] = risk; tp[jj] = tgt
                continue
        above = lv[lv > c[k]]
        if len(above):
            L = above[0]
            if h[k] >= L - 0.25 * a and uw >= wick * max(body, 0.05) and c[k] < h[k] - 0.5 * rng and (not trend or up4 is False):
                risk = (L + sl_atr * a) - c[k]
                if rr > 0:
                    tgt = rr * risk
                else:
                    bel = lv[lv < c[k] - risk]
                    tgt = (c[k] - bel[-1]) if len(bel) else 0
                if risk > 0 and tgt >= risk:
                    jj = b['last'][k]; sig[jj] = -1; sl[jj] = risk; tp[jj] = tgt
    return sig, tp, sl
