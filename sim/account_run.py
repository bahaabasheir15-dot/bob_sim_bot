#!/usr/bin/env python3
"""Run full-account simulations (deposit, compounding lot, all risk caps) and report money per year and month.

    python3 -m sim.account_run m1.npz "[('name', {params}), ...]"
"""
import collections
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


def _run(args):
    name, p = args
    s = Sim(_M1, p)
    tr = s.run()
    f = lambda t: dt.datetime.utcfromtimestamp(t).strftime('%Y.%m')
    bal = s.p['deposit']
    pk = bal
    dd = 0.0
    month = collections.defaultdict(float)
    year = collections.defaultdict(float)
    start_of_month = {}
    for x in sorted(tr, key=lambda x: x.t_close):
        m = f(x.t_close)
        start_of_month.setdefault(m, bal)
        bal += x.net
        pk = max(pk, bal)
        dd = max(dd, (pk - bal) / pk)
        month[m] += x.net
        year[m[:4]] += x.net
    pct = {m: month[m] / start_of_month[m] * 100 for m in month}
    gw = sum(x.net for x in tr if x.net > 0)
    gl = -sum(x.net for x in tr if x.net < 0)
    return name, dict(final=bal, dd=dd * 100, pf=gw / gl, year=dict(year), pct=pct, n=len(tr))


def main(data, runs):
    with mp.Pool(min(4, len(runs)), initializer=_init, initargs=(data,)) as pool:
        res = pool.map(_run, runs)
    for name, r in res:
        p = sorted(r['pct'].values())
        print(f"{name:22s} final {r['final']:9.0f}  maxDD {r['dd']:5.1f}%  PF {r['pf']:.2f}  trades {r['n']}")
        print('   by year $: ' + '  '.join(f'{y}: {v:+.0f}' for y, v in sorted(r['year'].items())))
        print(f"   monthly % : median {np.median(p):+.1f}%  worst {p[0]:+.1f}%  best {p[-1]:+.1f}%  losing {sum(v < 0 for v in p)}/{len(p)}")
        print('   ' + ' '.join(f"{m[2:]}:{v:+.0f}%" for m, v in sorted(r['pct'].items())))


if __name__ == '__main__':
    main(sys.argv[1], eval(sys.argv[2]))
