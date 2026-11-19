#!/usr/bin/env python3
"""Run the v39 simulator.

    python3 -m sim.run DATA_DIR|mt5_m1_export.csv 2026-01-01 2026-11-19 [--csv mt5_trades.csv] [--set key=value ...]

--csv  compares the simulated trades with an MT5 v39 trade log (HiWin_v39_trades*.csv)
--set  overrides any parameter of sim.hiwin_sim.DEFAULTS, e.g. --set recover_tp_atr=0
"""
import argparse
import collections
import csv
import datetime as dt
import time

from .data import load, load_mt5_csv
from .hiwin_sim import DEFAULTS, Sim, summary


def fmt(t):
    return dt.datetime.utcfromtimestamp(t).strftime('%Y.%m.%d %H:%M')


def per_tag(trades):
    g = collections.defaultdict(list)
    for x in trades:
        g[x.tag].append(x)
    out = {}
    for k, v in sorted(g.items()):
        n01 = sum(x.net / x.lots * 0.01 for x in v)
        out[k] = (len(v), round(sum(x.net for x in v)), round(n01))
    return out


def compare(trades, path):
    mt = [r for r in csv.DictReader(open(path)) if r['tag'] in ('S1', 'S5', 'B1')]
    st = [x for x in trades if x.tag in ('S1', 'S5', 'B1')]
    def key(t):
        return int(dt.datetime.strptime(t, '%Y.%m.%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp())
    used = set()
    hit = 0
    for r in mt:
        t0 = key(r['open_time'])
        best = None
        for i, x in enumerate(st):
            if i in used or x.tag != r['tag'] or x.buy != (r['side'] == 'buy'):
                continue
            if abs(x.t_open - t0) <= 600:
                best = i
                break
        if best is not None:
            used.add(best)
            hit += 1
    print(f'MT5 trades {len(mt)}  sim trades {len(st)}  matched {hit} '
          f'({hit / max(1, len(mt)) * 100:.0f}% of MT5, {hit / max(1, len(st)) * 100:.0f}% of sim)')
    by = collections.Counter(r['tag'] for r in mt)
    print('MT5 by tag', dict(by), ' sim by tag', dict(collections.Counter(x.tag for x in st)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data')
    ap.add_argument('start')
    ap.add_argument('end')
    ap.add_argument('--csv')
    ap.add_argument('--set', nargs='*', default=[])
    a = ap.parse_args()
    over = {}
    for kv in a.set:
        k, v = kv.split('=')
        over[k] = type(DEFAULTS[k])(v) if not isinstance(DEFAULTS[k], bool) else v.lower() in ('1', 'true')
    t0 = time.time()
    if a.data.lower().endswith(('.csv', '.txt')):
        m1 = load_mt5_csv(a.data)
        lo = int(dt.datetime.fromisoformat(a.start).replace(tzinfo=dt.timezone.utc).timestamp())
        hi = int(dt.datetime.fromisoformat(a.end).replace(tzinfo=dt.timezone.utc).timestamp()) + 86400
        keep = (m1['t'] >= lo) & (m1['t'] < hi)
        m1 = {k: v[keep] for k, v in m1.items()}
    else:
        m1 = load(a.data, a.start, a.end)
    s = Sim(m1, over)
    tr = s.run()
    print(f'minutes {len(m1["t"])}  run {time.time() - t0:.0f}s')
    print('summary', summary(tr, s.p['deposit']))
    print('by tag (n, net$, net per 0.01)', per_tag(tr))
    mon = collections.defaultdict(float)
    for x in tr:
        mon[fmt(x.t_open)[:7]] += x.net / x.lots * 0.01
    print('month per 0.01', {k: round(v) for k, v in sorted(mon.items())})
    if a.csv:
        compare(tr, a.csv)


if __name__ == '__main__':
    main()
