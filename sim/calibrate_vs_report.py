#!/usr/bin/env python3
"""Compare the simulator with an MT5 tester report, trade by trade.

    python3 -m sim.calibrate_vs_report m1.npz|m1.csv report.html "{'use_b1':False}"
"""
import collections
import datetime as dt
import sys

import numpy as np

from .data import load_mt5_csv
from .hiwin_sim import Sim


def load_m1(path):
    if path.endswith('.npz'):
        z = np.load(path)
        return {k: z[k] for k in z.files}
    return load_mt5_csv(path)


def main(data, report, over):
    sys.path.insert(0, 'analysis')
    import analyze_tester_report as A
    m1 = load_m1(data)
    s = Sim(m1, over)
    tr = s.run()
    d, o = A.load(report)
    MT = A.build_trades(d)
    f = lambda t: dt.datetime.utcfromtimestamp(t).strftime('%Y.%m.%d %H:%M:%S')
    first, last = MT[0]['tin'][:10], MT[-1]['tin'][:10]
    lo = (dt.datetime.strptime(first, '%Y.%m.%d') + dt.timedelta(days=3)).strftime('%Y.%m.%d')
    mt = [t for t in MT if lo <= t['tin'] and t['kind'] in ('S1', 'S5', 'B')]
    st = [x for x in tr if lo <= f(x.t_open) <= last + ' 23:59:59' and x.tag in ('S1', 'S5', 'B1')]
    P = lambda s_: dt.datetime.strptime(s_, '%Y.%m.%d %H:%M:%S')
    used, hit = set(), []
    for t in mt:
        tag = 'B1' if t['kind'] == 'B' else t['kind']
        for i, x in enumerate(st):
            if i in used or x.tag != tag or x.buy != (t['side'] == 'buy'):
                continue
            if abs((P(f(x.t_open)) - P(t['tin'])).total_seconds()) <= 600:
                used.add(i); hit.append((t, x)); break
    print('MT5', dict(collections.Counter('B1' if t['kind'] == 'B' else t['kind'] for t in mt)),
          ' SIM', dict(collections.Counter(x.tag for x in st)))
    print(f'matched {len(hit)} = {len(hit) / len(mt) * 100:.0f}% of MT5, {len(hit) / max(1, len(st)) * 100:.0f}% of sim;'
          f' same outcome {sum((t["net"] > 0) == (x.net > 0) for t, x in hit)}/{len(hit)}')
    ym = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    for t in MT:
        ym[t['tin'][:4]][0] += t['n01']; ym[t['tout'][:4]][2] += t['net']
    for x in tr:
        ym[f(x.t_open)[:4]][1] += x.net / x.lots * 0.01; ym[f(x.t_close)[:4]][3] += x.net
    print('year: per0.01 MT5 / SIM   |   $ MT5 / SIM')
    for y in sorted(ym):
        a = ym[y]
        print(f'  {y}: {a[0]:7.0f} / {a[1]:7.0f}   | {a[2]:8.0f} / {a[3]:8.0f}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], eval(sys.argv[3]) if len(sys.argv) > 3 else {})
