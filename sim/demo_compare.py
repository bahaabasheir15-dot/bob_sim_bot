#!/usr/bin/env python3
"""Weekly demo check: compare a live/demo MT5 account report with the simulator, trade by trade.

    python3 -m sim.demo_compare report.html [m1_export.csv] [--shift -1] [--from 2026.11.20] [--params "{...}"]

report.html  MT5 account report (History tab > right click > Report > HTML) or a tester report.
m1_export    MT5 M1 bars export (Symbols > Bars > Export) that covers the demo weeks. Its bars are
             appended to data/xauusd_plus_m1_2023_2026.npz. Without it only the npz is used.
--shift      InpHourShift of the account (IFCMarkets = -1). Demo times are moved to Vantage time.
--from       first day to compare (default: first EA trade in the report).
--params     simulator overrides on top of v45.2.

The simulator starts 45 days before the first compared day (indicator warm-up) with the demo's
starting balance, so its lot sizes are close but not identical; money is compared per demo lot.
"""
import argparse
import collections
import datetime as dt
import html as h
import re

import numpy as np

from .data import load_mt5_csv, load_npz
from .hiwin_sim import Sim

NPZ = 'data/xauusd_plus_m1_2023_2026.npz'
V452 = dict(use_b1=False, atr_hard_min_pct=0.14, recover_tp_atr=0.0, use_ldn=True, use_s4=True, use_trend=True,
            tr_risk_pct=0.25, ldn_sl_mult=1.75, sl_atr=7.0, tr_max_minlot_risk=1.0, use_night=True,
            night_sl_pct=0.5, night_min_prev_pct=1.0, night_lot_mult=1.0)
FMT = '%Y.%m.%d %H:%M:%S'
WINDOW = 600          # seconds: a demo trade and a simulator trade match if they open this close


def num(s):
    s = s.replace(' ', '').replace('\xa0', '').replace(',', '')
    if not s:
        return 0.0
    neg = s.endswith('-')
    return -float(s.rstrip('-')) if neg else float(s)


def ts(s):
    return int(dt.datetime.strptime(s[:19], FMT).replace(tzinfo=dt.timezone.utc).timestamp())


def fmt(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%m.%d %H:%M')


def load_deals(path):
    """Deals table of an MT5 report. Works with account reports (Commission, Fee, Swap, Profit, Balance,
    Comment) and tester reports (no Fee): money columns are read from the end of the row."""
    raw = open(path, 'rb').read()
    s = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8', 'replace')
    deals, deposit = [], None
    for row in re.findall(r'<tr.*?</tr>', s, flags=re.S | re.I):
        c = [h.unescape(re.sub(r'<.*?>', '', x)).strip()
             for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, flags=re.S | re.I)]
        if len(c) < 12 or not re.match(r'\d{4}\.\d\d\.\d\d \d\d:\d\d', c[0]):
            continue
        if c[3].lower() == 'balance' and deposit is None:
            deposit = num(c[-2])
            continue
        if c[4] not in ('in', 'out', 'in/out') or c[3] not in ('buy', 'sell'):
            continue
        # c: time deal symbol type dir vol price order <money...> profit balance comment
        money = [num(x) for x in c[8:-3]]          # commission, (fee), swap
        deals.append(dict(t=c[0], side=c[3], io=c[4], vol=num(c[5]), price=num(c[6]), order=c[7],
                          pl=num(c[-3]), comm=sum(money), cm=c[-1], sym=c[2]))
    return deals, deposit


def build_trades(deals):
    """Pair each exit with the open position of the opposite side and same volume whose
    price arithmetic best explains the profit."""
    open_, out = [], []
    for d in deals:
        if d['io'] == 'in':
            open_.append(d)
            continue
        cands = [p for p in open_ if p['side'] != d['side'] and abs(p['vol'] - d['vol']) < 1e-9] or \
                [p for p in open_ if p['side'] != d['side']]
        if not cands:
            continue
        sg = lambda p: 1 if p['side'] == 'buy' else -1
        p = min(cands, key=lambda p: abs((d['price'] - p['price']) * sg(p) * d['vol'] * 100 - d['pl']))
        open_.remove(p)
        tag = p['cm'].split()[0] if p['cm'] else '?'
        fam = 'R' if tag.startswith('R') else tag
        ex = d['cm'].lower()
        out.append(dict(tag=fam, buy=p['side'] == 'buy', vol=d['vol'], op=p['price'], cp=d['price'],
                        t_open=ts(p['t']), t_close=ts(d['t']), net=d['pl'] + d['comm'] + p['comm'],
                        exit='tp' if ex.startswith('tp') else 'sl' if ex.startswith('sl') else 'ea'))
    return out, open_


def load_m1(csv):
    m1 = load_npz(NPZ)
    if not csv:
        return m1
    x = load_mt5_csv(csv)
    keep = x['t'] > m1['t'][-1]
    return {k: np.concatenate((m1[k], x[k][keep])) for k in m1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report')
    ap.add_argument('m1', nargs='?')
    ap.add_argument('--shift', type=int, default=0)
    ap.add_argument('--from', dest='start')
    ap.add_argument('--params', default='{}')
    a = ap.parse_args()

    deals, deposit = load_deals(a.report)
    demo, still_open = build_trades(deals)
    for x in demo:                                   # broker clock -> Vantage clock
        x['t_open'] -= a.shift * 3600
        x['t_close'] -= a.shift * 3600
    start = ts(a.start.replace('-', '.') + ' 00:00:00') if a.start else min(x['t_open'] for x in demo) // 86400 * 86400
    demo = [x for x in demo if x['t_open'] >= start]

    m1 = load_m1(a.m1)
    end = int(m1['t'][-1])
    late = [x for x in demo if x['t_open'] > end]
    demo = [x for x in demo if x['t_open'] <= end]
    sl = slice(np.searchsorted(m1['t'], start - 45 * 86400), None)
    m1 = {k: v[sl] for k, v in m1.items()}
    p = dict(V452, deposit=deposit or 5000.0, **eval(a.params))
    sim = [x for x in Sim(m1, p).run() if start <= x.t_open <= end]

    used, pairs = set(), []
    for d in sorted(demo, key=lambda x: x['t_open']):
        best = None
        for i, s in enumerate(sim):
            if i in used or s.buy != d['buy'] or (s.tag if s.tag != 'R' else 'R') != d['tag']:
                continue
            gap = abs(s.t_open - d['t_open'])
            if gap <= WINDOW and (best is None or gap < best[0]):
                best = (gap, i)
        if best:
            used.add(best[1])
            pairs.append((d, sim[best[1]]))
        else:
            pairs.append((d, None))
    extra = [s for i, s in enumerate(sim) if i not in used]

    print(f'period {fmt(start)} .. {fmt(end)} (Vantage time)   deposit {deposit}   shift {a.shift}')
    if late:
        print(f'!! {len(late)} demo trades are after the end of the price data ({fmt(end)}): send the M1 export')
    if still_open:
        print(f'still open at report time: {len(still_open)}')
    print('\n time         tag  side  demo$    sim$*   entry diff  exit demo/sim')
    for d, s in pairs:
        side = 'buy ' if d['buy'] else 'sell'
        if s is None:
            print(f" {fmt(d['t_open'])}  {d['tag']:3s}  {side} {d['net']:7.2f}    ----   NOT IN SIM")
            continue
        sn = s.net / s.lots * d['vol']
        diff = (d['op'] - s.op) * (1 if d['buy'] else -1)
        print(f" {fmt(d['t_open'])}  {d['tag']:3s}  {side} {d['net']:7.2f} {sn:8.2f}   {diff:+6.2f}      {d['exit']}/{s.exit}")
    for s in extra:
        print(f" {fmt(s.t_open)}  {s.tag:3s}  {'buy ' if s.buy else 'sell'}    ----  {s.net:8.2f}   ONLY IN SIM ({s.lots} lot)")

    print('\n engine  demo  sim  matched  demo$     sim$*')
    eng = sorted({d['tag'] for d in demo} | {s.tag for s in sim})
    for e in eng:
        dd = [x for x in demo if x['tag'] == e]
        ss = [x for x in sim if x.tag == e]
        mp = [(d, s) for d, s in pairs if s is not None and d['tag'] == e]
        sm = sum(s.net / s.lots * d['vol'] for d, s in mp) + sum(x.net for x in extra if x.tag == e)
        print(f' {e:6s} {len(dd):5d} {len(ss):4d} {len(mp):6d}  {sum(x["net"] for x in dd):8.2f} {sm:9.2f}')
    m = sum(s is not None for _, s in pairs)
    print(f'\n matched {m}/{len(demo)} demo trades ({m / max(1, len(demo)) * 100:.0f}%), '
          f'{m}/{len(sim)} sim trades ({m / max(1, len(sim)) * 100:.0f}%)')
    same = sum((d['net'] > 0) == (s.net > 0) for d, s in pairs if s is not None)
    print(f' same win/loss {same}/{m}')
    diffs = [(d['op'] - s.op) * (1 if d['buy'] else -1) for d, s in pairs if s is not None]
    if diffs:
        print(f' entry price vs sim: average {np.mean(diffs):+.2f}$ (positive = demo paid more)')
    print(' * sim$ = simulator profit scaled to the demo lot size')


if __name__ == '__main__':
    main()
