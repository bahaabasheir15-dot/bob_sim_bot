#!/usr/bin/env python3
"""Deep analysis of an MT5 Strategy Tester report (PDF, Arabic or English UI)
for the XAU HiWin EA family.

    python3 analyze_tester_report.py report.pdf

Needs `pdftotext` (poppler-utils). It rebuilds every closed trade from the
deals table, rebuilds each scalp + recovery-leg GROUP, and prints the tables
the v39 decision was based on. All money figures are also normalised to a
fixed 0.01 lot ("per0.01") so compounding does not hide what each rule does.
"""
import collections
import datetime as dt
import re
import subprocess
import sys

DEAL_RX = re.compile(
    r'^\s*(.*?)\s+([\d,]+\.\d\d)\s+(-?[\d,]+\.\d\d-?)\s+([\d.]+-?)\s+([\d.]+-?)\s+(\d+)\s+'
    r'([\d.]+)\s+([\d.]+)\s+(in|out)\s+(buy|sell)\s+\S*XAUUSD\S*\s+(\d+)\s+'
    r'(\d\d:\d\d:\d\d) (\d{4}\.\d\d\.\d\d)')
ORDER_RX = re.compile(
    r'^\s*(.*?)\s+(filled|canceled)\s+(\d\d:\d\d:\d\d \d{4}\.\d\d\.\d\d)\s+(?:([\d.]+)\s+)?(?:([\d.]+)\s+)?'
    r'([\d.]+)\s+([\d.]+) / ([\d.]+)\s+(buy limit|sell limit|buy|sell)\s+\S*XAUUSD\S*\s+(\d+)\s+'
    r'(\d\d:\d\d:\d\d \d{4}\.\d\d\.\d\d)')
SL_ATR = 5.0   # InpSLatr of the scalper: ATR at entry = |limit price - SL| / SL_ATR


def num(s):
    s = s.replace(',', '')
    neg = s.endswith('-')
    v = float(s.rstrip('-'))
    return -v if neg else v


def ptime(s):
    return dt.datetime.strptime(s, '%Y.%m.%d %H:%M:%S')


def flip(s):  # "08:50:00 2026.01.08" -> "2026.01.08 08:50:00"
    a, b = s.split()
    return f'{b} {a}'


def load(pdf):
    text = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True,
                          text=True, check=True).stdout.replace('\f', '').split('\n')
    deals, orders = [], {}
    for line in text:
        m = DEAL_RX.match(line)
        if m:
            g = m.groups()
            deals.append(dict(cm=g[0].strip(), pl=num(g[2]), comm=num(g[4]), order=int(g[5]),
                              price=float(g[6]), vol=float(g[7]), io=g[8], side=g[9],
                              t=f'{g[12]} {g[11]}'))
            continue
        m = ORDER_RX.match(line)
        if m:
            g = m.groups()
            orders[int(g[9])] = dict(sl=g[4], price=float(g[5]), setup=flip(g[10]))
    return deals, orders


def build_trades(deals):
    """Pair each exit deal with the open position whose arithmetic matches its profit."""
    open_, trades = [], []
    for d in deals:
        if d['io'] == 'in':
            open_.append(d)
            continue
        cands = [p for p in open_ if p['side'] != d['side'] and abs(p['vol'] - d['vol']) < 1e-9]

        def err(p):
            sg = 1 if p['side'] == 'buy' else -1
            return abs((d['price'] - p['price']) * sg * p['vol'] * 100 - d['pl'])
        p = min(cands, key=err)
        open_.remove(p)
        net = d['pl'] + d['comm'] + p['comm']
        tag = p['cm']
        trades.append(dict(tag=tag, kind=tag[0] if tag[:1] in ('R', 'B') else tag, side=p['side'],
                           tin=p['t'], tout=d['t'], order=p['order'], vol=d['vol'], net=net,
                           n01=net / d['vol'] * 0.01,
                           exit='tp' if d['cm'].startswith('tp') else 'sl' if d['cm'].startswith('sl') else 'time/ea'))
    return trades


def groups(trades, orders):
    legs = {int(t['tag'][1:]): t for t in trades if t['kind'] == 'R'}
    out = []
    for t in trades:
        if t['kind'] in ('R', 'B'):
            continue
        o = orders.get(t['order'])
        g = dict(t)
        g['atr'] = abs(float(o['sl']) - o['price']) / SL_ATR if o and o['sl'] else 0.0
        leg = legs.get(t['order'])
        g['rescued'] = leg is not None
        g['gnet'] = t['net'] + (leg['net'] if leg else 0)
        g['g01'] = g['gnet'] / t['vol'] * 0.01
        g['gexit'] = leg['exit'] if leg else t['exit']
        g['gend'] = leg['tout'] if leg else t['tout']
        out.append(g)
    return out


def curve(units):
    ev = sorted(units, key=lambda u: u['gend'])
    eq = pk = dd = 0.0
    for u in ev:
        eq += u['g01']
        pk = max(pk, eq)
        dd = max(dd, pk - eq)
    gw = sum(u['g01'] for u in units if u['g01'] > 0)
    gl = -sum(u['g01'] for u in units if u['g01'] < 0)
    days = len({u['tin'][:10] for u in units})
    return (f"n={len(units):4d} net/0.01={eq:7.0f} maxDD/0.01={dd:5.0f} RF={eq / dd if dd else 0:5.2f} "
            f"PF={gw / gl if gl else 99:5.2f} days={days}")


def main(pdf):
    deals, orders = load(pdf)
    trades = build_trades(deals)
    g = groups(trades, orders)
    b1 = [dict(t, g01=t['n01'], gend=t['tout']) for t in trades if t['kind'] == 'B']
    print(f'deals {len(deals)}  trades {len(trades)}  scalp groups {len(g)}  B1 {len(b1)}\n')

    print('== 1. where the money comes from (account currency, compounding included)')
    clean = [x for x in g if not x['rescued']]
    res = [x for x in g if x['rescued']]
    print(f"  scalps that never needed a leg : {len(clean):4d}  net {sum(x['gnet'] for x in clean):+10.0f}")
    for e in ('tp', 'sl', 'time/ea'):
        s = [x for x in res if x['gexit'] == e]
        print(f"  rescued groups ending {e:8s}: {len(s):4d}  net {sum(x['gnet'] for x in s):+10.0f}")
    print(f"  recovery legs alone           : {len(res):4d}  net "
          f"{sum(t['net'] for t in trades if t['kind'] == 'R'):+10.0f}")
    print(f"  B1 breakout                   : {len(b1):4d}  net {sum(t['net'] for t in b1):+10.0f}\n")

    print('== 2. scalp groups by ATR at the signal (per 0.01 lot)')
    for lo, hi in [(0, 5.5), (5.5, 6), (6, 6.5), (6.5, 7), (7, 8), (8, 999)]:
        s = [x for x in g if lo <= x['atr'] < hi]
        if s:
            bad = sum(1 for x in s if x['rescued'] and x['gexit'] != 'tp')
            print(f'  ATR {lo:4.1f}-{hi:<5.1f} {curve(s)} bad groups={bad}')
    print()

    print('== 3. whole EA (scalp groups + B1), per 0.01 lot, by ATR hard floor')
    for th in (0, 5.5, 6, 6.5, 7):
        print(f'  floor {th:4.1f}: {curve([x for x in g if x["atr"] >= th] + b1)}')
    print()

    print('== 4. same split on each half of the test (is it one bad stretch?)')
    months = sorted({x['tin'][:7] for x in g})
    mid = months[len(months) // 2]
    for name, sel in (('first half ', lambda x: x['tin'][:7] < mid), ('second half', lambda x: x['tin'][:7] >= mid)):
        s = [x for x in g if sel(x)]
        r = [x for x in s if x['rescued']]
        ok = sum(1 for x in r if x['gexit'] == 'tp')
        print(f"  {name} ATR<5.5 : {curve([x for x in s if x['atr'] < 5.5])}")
        print(f"  {name} ATR>=5.5: {curve([x for x in s if x['atr'] >= 5.5])}")
        print(f"  {name} rescue success {ok}/{len(r)} = {ok / max(1, len(r)) * 100:.0f}%")
    print()

    print('== 5. month by month, per 0.01 lot')
    by = collections.defaultdict(float)
    for x in g + b1:
        by[x['tin'][:7]] += x['g01']
    print('  ' + '  '.join(f'{k[5:]}:{v:+.0f}' for k, v in sorted(by.items())))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
