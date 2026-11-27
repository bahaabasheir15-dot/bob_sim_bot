#!/usr/bin/env python3
"""Stand-alone fast scalping engines on M1 bars (research for a separate experimental scalping bot).

Each engine: signal at the close of M1 bar i, market entry at the open of bar i+1 (buy at ask, sell at bid),
exit by TP / SL (if both inside one bar -> SL, the worst case) or time stop; one position per engine at a time.
P&L per 0.01 lot = price move x 1 oz, minus commission 0.06 $ (3 $/lot/side) and an optional extra slippage.

    python3 -m sim.fast_scalp data/xauusd_plus_m1_2023_2026.npz
"""
import datetime as dt
import sys

import numpy as np

from . import indicators as ind
from .data import load_npz

COMM = 0.06


def _hours(t):
    return (t % 86400) // 3600, (t % 86400) // 60


def run(m, sig, tp_d, sl_d, max_min, slip=0.0, sp_mult=1.0):
    """sig: +1/-1/0 per bar (decided at bar close), tp_d/sl_d: distances (price) per bar. Returns trades list."""
    bo, bh, bl, bc = m['bo'], m['bh'], m['bl'], m['bc']
    sp = (m['ac'] - m['bc']) * sp_mult
    t = m['t']
    n = len(t)
    out = []
    i = 0
    idx = np.flatnonzero(sig != 0)
    p = 0
    while p < len(idx):
        i = idx[p]
        if i + 1 >= n:
            break
        d = sig[i]
        j = i + 1
        if t[j] - t[i] > 600:          # gap (weekend / session break): skip
            p += 1
            continue
        op = bo[j] + (sp[j] if d == 1 else 0.0)
        tp = op + d * tp_d[i]
        sl = op - d * sl_d[i]
        k = j
        res = None
        while k < n:
            # bid path for longs; ask = bid + spread for shorts
            if d == 1:
                if bl[k] <= sl:
                    res = (min(sl, bo[k]) if k > j else sl, k)
                    break
                if bh[k] >= tp:
                    res = (max(tp, bo[k]) if k > j and bo[k] > tp else tp, k)
                    break
            else:
                a_h, a_l, a_o = bh[k] + sp[k], bl[k] + sp[k], bo[k] + sp[k]
                if a_h >= sl:
                    res = (max(sl, a_o) if k > j else sl, k)
                    break
                if a_l <= tp:
                    res = (min(tp, a_o) if k > j and a_o < tp else tp, k)
                    break
            if t[k] - t[j] >= max_min * 60 or (k + 1 < n and t[k + 1] - t[k] > 600):
                res = (bc[k] if d == 1 else bc[k] + sp[k], k)
                break
            k += 1
        if res is None:
            break
        cp, k = res
        pnl = (cp - op) * d - COMM - slip
        out.append((int(t[j]), int(t[k]), d, pnl))
        p = np.searchsorted(idx, k + 1)          # next signal after the exit
    return out


def stats(tr, name):
    if not tr:
        print(f'{name:34s} no trades'); return
    yrs = np.array([dt.datetime.utcfromtimestamp(x[0]).year for x in tr])
    v = np.array([x[3] for x in tr])
    eq = np.cumsum(v); dd = (np.maximum.accumulate(eq) - eq).max()
    days = {x[0] // 86400 for x in tr}
    dayp = {}
    for x in tr:
        dayp[x[1] // 86400] = dayp.get(x[1] // 86400, 0) + x[3]
    dv = np.array(list(dayp.values()))
    ys = ' '.join(f'{v[yrs == y].sum():7.0f}' for y in (2023, 2024, 2025, 2026))
    hold = np.median([(x[1] - x[0]) / 60 for x in tr])
    print(f'{name:34s} n{len(tr):6d} {len(tr) / len(days):4.1f}/d hold{hold:4.0f}m win{(v > 0).mean() * 100:5.1f}% | {ys} | '
          f'{v.sum():7.0f} DD {dd:5.0f} winDays {(dv > 0).mean() * 100:4.1f}%', flush=True)


def signals(m):
    c, h, l, o = m['bc'], m['bh'], m['bl'], m['bo']
    t = m['t']
    hr, mi = _hours(t)
    a = ind.atr(h, l, c, 14)
    S = {}
    # E1: Bollinger fade (M1, 20, k) + RSI(7) extreme, back to the mid band
    mid = ind.sma(c, 20)
    sd = np.full(len(c), np.nan)
    sd[19:] = np.lib.stride_tricks.sliding_window_view(c, 20).std(axis=1)
    r7 = ind.rsi(c, 7)
    for k_ in (2.5, 3.0):
        for win, (h0, h1) in (('all', (1, 22)), ('asia', (1, 9)), ('eu-us', (10, 20))):
            sig = np.zeros(len(c), np.int8)
            ok = (hr >= h0) & (hr <= h1)
            sig[ok & (c < mid - k_ * sd) & (r7 < 20)] = 1
            sig[ok & (c > mid + k_ * sd) & (r7 > 80)] = -1
            S[f'E1 BB{k_} {win}'] = (sig, np.abs(c - mid), 2.0 * k_ * sd)
    # E2: session opening-range micro breakout (first 15 min after 10:00 and 16:30 server), TP = 1 range, SL = range
    sig = np.zeros(len(c), np.int8); rng = np.zeros(len(c))
    day = t // 86400
    for (sh, sm) in ((10, 0), (16, 30)):
        st = sh * 60 + sm
        inbox = (mi >= st) & (mi < st + 15)
        after = (mi >= st + 15) & (mi < st + 120)
        ud = np.unique(day)
        hi = {}; lo = {}
        for dd_, hh, ll in zip(day[inbox], h[inbox], l[inbox]):
            hi[dd_] = max(hi.get(dd_, -1e9), hh); lo[dd_] = min(lo.get(dd_, 1e9), ll)
        done = set()
        for i in np.flatnonzero(after):
            dd_ = day[i]
            if dd_ not in hi or (dd_, st) in done:
                continue
            if c[i] > hi[dd_]:
                sig[i] = 1
            elif c[i] < lo[dd_]:
                sig[i] = -1
            else:
                continue
            rng[i] = max(hi[dd_] - lo[dd_], 0.5); done.add((dd_, st))
    S['E2 ORB 10:00+16:30'] = (sig, rng, rng)
    # E3: M1 momentum burst: body > 2.5 ATR closing near its extreme -> continuation, TP 1 ATR, SL 1.5 ATR
    body = c - o
    sig = np.zeros(len(c), np.int8)
    ok = (hr >= 9) & (hr <= 20)
    sig[ok & (body > 2.5 * a) & (c - l > 0.8 * (h - l))] = 1
    sig[ok & (-body > 2.5 * a) & (h - c > 0.8 * (h - l))] = -1
    S['E3 burst follow'] = (sig, 1.0 * a, 1.5 * a)
    S['E3b burst FADE'] = (-sig, 1.0 * a, 2.0 * a)
    return S


def main(path):
    m = load_npz(path)
    S = signals(m)
    for name, (sig, tp, sl) in S.items():
        tp = np.nan_to_num(tp); sl = np.nan_to_num(sl)
        sig = np.where((tp > 0.05) & (sl > 0.05), sig, 0)
        stats(run(m, sig, tp, sl, 30), name)


if __name__ == '__main__':
    main(sys.argv[1])
