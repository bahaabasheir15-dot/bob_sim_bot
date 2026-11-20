#!/usr/bin/env python3
"""Run many parameter variants on the same M1 data in parallel, fixed 0.01 lot,
and print per-year results so a change has to hold up in EVERY year.

    python3 -m sim.research m1.npz "BASE_DICT" "[('name', {overrides}), ...]"
"""
import datetime as dt
import multiprocessing as mp
import sys

import numpy as np

from .hiwin_sim import Sim

_M1 = None


def _init(path):
    global _M1
    from .data import load_npz
    _M1 = load_npz(path)


def year_stats(tr, years=('2023', '2024', '2025', '2026')):
    f = lambda t: dt.datetime.utcfromtimestamp(t).strftime('%Y.%m')
    out = {}
    for y in list(years) + ['ALL']:
        L = sorted((x for x in tr if y == 'ALL' or f(x.t_open)[:4] == y), key=lambda x: x.t_close)
        eq = pk = dd = 0.0
        for x in L:
            eq += x.net / x.lots * 0.01
            pk = max(pk, eq)
            dd = max(dd, pk - eq)
        gw = sum(x.net / x.lots for x in L if x.net > 0)
        gl = -sum(x.net / x.lots for x in L if x.net < 0)
        months = {}
        for x in L:
            months[f(x.t_open)] = months.get(f(x.t_open), 0) + x.net / x.lots * 0.01
        out[y] = dict(n=len(L), net=eq, dd=dd, pf=gw / gl if gl else 99, losem=sum(v < 0 for v in months.values()))
    return out


def _run(args):
    name, p = args
    tr = Sim(_M1, p).run()
    return name, year_stats(tr)


def main(data, base, variants):
    jobs = [(n, dict(base, fixed_lot=0.01, **v)) for n, v in variants]
    with mp.Pool(4, initializer=_init, initargs=(data,)) as pool:
        res = pool.map(_run, jobs)
    print(f"{'variant':26s} {'2023':>11s} {'2024':>11s} {'2025':>11s} {'2026':>11s} | {'ALL net':>7s} {'DD':>5s} {'RF':>5s} {'PF':>5s} {'n':>5s} lossM")
    for name, r in res:
        cells = ' '.join(f"{r[y]['net']:6.0f}/{r[y]['dd']:<4.0f}" for y in ('2023', '2024', '2025', '2026'))
        a = r['ALL']
        print(f"{name:26s} {cells} | {a['net']:7.0f} {a['dd']:5.0f} {a['net'] / max(a['dd'], 1):5.2f} {a['pf']:5.2f} {a['n']:5d} {a['losem']:3d}")


if __name__ == '__main__':
    main(sys.argv[1], eval(sys.argv[2]), eval(sys.argv[3]))
