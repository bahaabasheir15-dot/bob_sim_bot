"""Engine X (idea taken from the Gold Beaver EA, MQL5 product 177869, reverse-engineered from its tester report):
long Donchian channel of H4 candles, stop orders at the channel high/low refreshed at every H4 open,
stop loss and target in % of price, fast break-even. Fixed 0.01 lot, M1 path (4 points per minute).

    python3 -m sim.swing_breakout data/xauusd_plus_m1_2023_2026.npz "[('name', {kwargs}), ...]"
"""
import datetime as dt
import multiprocessing as mp
import sys

import numpy as np

from .data import load_npz, resample

COMM = 0.06
_M = None


def run(m, n=96, sl_pct=0.45, tp_pct=0.5, be_pct=0.15, be_lock_pct=0.02, buf=0.2, expiry_h=168,
        stack=1, both=True, trail_pct=0.0, start=None, slip=0.0):
    t = m['t']; bo, bh, bl, bc = m['bo'], m['bh'], m['bl'], m['bc']; ao, ah, al, ac = m['ao'], m['ah'], m['al'], m['ac']
    H = resample(m, 240)
    hh = H['h']; ll = H['l']; ht = H['t']
    h4_of = np.searchsorted(ht, t, side='right') - 1
    pend = []      # dict(d, lv, exp)
    pos = []       # dict(d, op, sl, tp, be, t0)
    out = []
    last_k = -1
    for j in range(len(t)):
        k = h4_of[j]
        if k != last_k:                                   # new H4 candle -> refresh the levels
            last_k = k
            if k > n:
                hi = hh[k - n:k].max() + buf; lo = ll[k - n:k].min() - buf
                pend = [p for p in pend if p['exp'] > t[j]]
                for d, lv in ((1, hi), (-1, lo)):
                    if not both and d == -1:
                        continue
                    same = [p for p in pend if p['d'] == d]
                    if stack <= 1:
                        pend = [p for p in pend if p['d'] != d]
                        pend.append(dict(d=d, lv=lv, exp=t[j] + expiry_h * 3600))
                    elif len(same) < stack:
                        pend.append(dict(d=d, lv=lv, exp=t[j] + expiry_h * 3600))
        if bc[j] >= bo[j]:
            path = ((bo[j], ao[j]), (bl[j], al[j]), (bh[j], ah[j]), (bc[j], ac[j]))
        else:
            path = ((bo[j], ao[j]), (bh[j], ah[j]), (bl[j], al[j]), (bc[j], ac[j]))
        for pi, (b, a) in enumerate(path):
            gap = pi == 0
            for p in list(pend):
                if (p['d'] == 1 and a >= p['lv']) or (p['d'] == -1 and b <= p['lv']):
                    op = (max(a, p['lv']) if p['d'] == 1 else min(b, p['lv'])) if gap else (a if p['d'] == 1 else b)
                    if not gap:
                        op = p['lv'] + (a - b) if p['d'] == 1 else p['lv']     # stop fills at its level (+spread for buys)
                    op += p['d'] * slip                                          # extra slippage on the stop fill
                    d = p['d']
                    pos.append(dict(d=d, op=op, sl=op - d * op * sl_pct / 100, tp=op + d * op * tp_pct / 100,
                                    be=False, t0=t[j], best=op))
                    pend.remove(p)
            for x in list(pos):
                d = x['d']; px = b if d == 1 else a
                hit = None
                if (d == 1 and b <= x['sl']) or (d == -1 and a >= x['sl']):
                    hit = px if gap else x['sl']
                elif (d == 1 and b >= x['tp']) or (d == -1 and a <= x['tp']):
                    hit = px if gap else x['tp']
                if hit is not None:
                    out.append((int(x['t0']), int(t[j]), d * (hit - x['op']) - COMM, d))
                    pos.remove(x); continue
                fav = (b - x['op']) if d == 1 else (x['op'] - a)
                x['best'] = max(x['best'], fav) if x['best'] != x['op'] else fav
                if not x['be'] and be_pct > 0 and fav >= x['op'] * be_pct / 100:
                    ns = x['op'] + d * x['op'] * be_lock_pct / 100
                    if (ns - x['sl']) * d > 0:
                        x['sl'] = ns
                    x['be'] = True
                if trail_pct > 0 and x['be']:
                    ns = (b if d == 1 else a) - d * x['op'] * trail_pct / 100
                    if (ns - x['sl']) * d > 0:
                        x['sl'] = ns
    return out


def report(name, out):
    s = []
    for Y in (2023, 2024, 2025, 2026):
        v = [x[2] for x in out if dt.datetime.utcfromtimestamp(x[0]).year == Y]
        s.append(f"{Y}:{sum(v):6.0f}/{len(v):3d}")
    v = np.array([x[2] for x in out]) if out else np.zeros(1)
    eq = np.cumsum([x[2] for x in sorted(out, key=lambda x: x[1])]) if out else np.zeros(1)
    dd = (np.maximum.accumulate(eq) - eq).max()
    pf = v[v > 0].sum() / max(-v[v < 0].sum(), 1e-9)
    return f"{name:30s} " + ' '.join(s) + f" | ALL {v.sum():6.0f} PF{pf:5.2f} DD{dd:5.0f} win{(v > 0).mean() * 100:3.0f}%"


def _init(path):
    global _M
    _M = load_npz(path)


def _job(a):
    name, kw = a
    return report(name, run(_M, **kw))


if __name__ == '__main__':
    with mp.Pool(4, initializer=_init, initargs=(sys.argv[1],)) as p:
        for r in p.imap(_job, eval(sys.argv[2])):
            print(r, flush=True)
