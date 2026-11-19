#!/usr/bin/env python3
"""What-if analysis on the v39 per-trade log (HiWin_v39_trades*.csv).

    python3 analyze_trade_log.py HiWin_v39_trades_XXXX.csv

Everything is in $ per 0.01 lot after commission, so compounding does not
blur the comparison. Exact (path-free) counterfactuals only:
  A) group stop X ATR beyond the recovery leg  (uses the original's MAE)
  B) no recovery leg, hard stop Y <= 2 ATR       (uses the original's MAE)
  C) lower group target t <= 0.75 ATR            (uses the leg's MFE)
"""
import sys
import csv,collections
F=sys.argv[1]
R=list(csv.DictReader(open(F)))
for r in R:
    for k in ['open_price','close_price','lots','atr_entry','net_pl','mae_atr','mfe_atr','min_to_mae','min_held']: r[k]=float(r[k])
    sg=1 if r['side']=='buy' else -1; r['sg']=sg
    r['p01']=(r['close_price']-r['open_price'])*sg-0.06     # $ per 0.01 lot, after commission
legs=collections.defaultdict(list)
for r in R:
    if r['tag'].startswith('R'): legs[r['tag'][1:]].append(r)
orig=[r for r in R if r['tag'] in('S1','S5')]; B1=[r for r in R if r['tag']=='B1']
print('orig',len(orig),'groups w/ leg',sum(1 for o in orig if o['pos_id'] in legs),'legs',sum(map(len,legs.values())))
def base(o):
    return o['p01']+sum(l['p01'] for l in legs.get(o['pos_id'],[]))
def ev(units):
    units=sorted(units,key=lambda u:u[0]);eq=pk=dd=0
    for t,v in units: eq+=v;pk=max(pk,eq);dd=max(dd,pk-eq)
    gw=sum(v for _,v in units if v>0);gl=-sum(v for _,v in units if v<0)
    return f"net={eq:7.0f} DD={dd:5.0f} RF={eq/dd:5.2f} PF={gw/gl:5.2f}"
def end(o): return max([o['close_time']]+[l['close_time'] for l in legs.get(o['pos_id'],[])])
b1u=[(r['close_time'],r['p01']) for r in B1]
print('BASE v39             ',ev([(end(o),base(o)) for o in orig]+b1u))
# check: per-group exit stats
G=[o for o in orig if o['pos_id'] in legs]
print('groups',len(G),'orig MAE quantiles of TP-groups:',sorted(round(o['mae_atr'],2) for o in G if o['exit']=='tp'))
# A) group stop X beyond leg
def gstop(o,X):
    L=legs.get(o['pos_id'])
    if not L: return base(o)
    a=o['atr_entry']; lp=L[0]['open_price']; stop=lp-o['sg']*X*a
    lvl=(o['open_price']-stop)*o['sg']/a   # ATR from original entry
    if lvl>=5 or o['mae_atr']<lvl-1e-9: return base(o)
    v=(stop-o['open_price'])*o['sg']-0.06
    for l in L: v+=(stop-l['open_price'])*o['sg']-0.06
    return v
for X in [0.5,1.0,1.5,2.0,2.5]:
    print(f'group stop X={X}      ',ev([(end(o),gstop(o,X)) for o in orig]+b1u))
# B) no rescue, hard stop Y ATR on the original
def hard(o,Y):
    if o['mae_atr']>=Y: return -Y*o['atr_entry']-0.06
    return base(o)
for Y in [1.0,1.5,2.0]:
    print(f'no rescue, stop {Y} ATR',ev([(end(o),hard(o,Y)) for o in orig]+b1u))
# C) lower group target t (ATR beyond the weighted average) - exact for t<=0.75
def gtp(o,t):
    L=legs.get(o['pos_id'])
    if not L: return base(o)
    l=L[0];a=o['atr_entry'];sg=o['sg']
    avg=(o['open_price']*o['lots']+l['open_price']*l['lots'])/(o['lots']+l['lots'])
    tp=avg+sg*t*a
    need=(tp-l['open_price'])*sg/a
    if l['mfe_atr']>=need-1e-9:
        return (tp-o['open_price'])*sg+(tp-l['open_price'])*sg*l['lots']/o['lots']-0.12
    return base(o)
for t in [0.75,0.5,0.25,0.0,-0.25]:
    conv=sum(1 for o in orig if o['pos_id'] in legs and legs[o['pos_id']][0]['exit']!='tp' and gtp(o,t)!=base(o))
    print(f'group target {t:5}    ',ev([(end(o),gtp(o,t)) for o in orig]+b1u),' failed->saved',conv)
fail=[o for o in orig if o['pos_id'] in legs and legs[o['pos_id']][0]['exit']!='tp']
print('failed groups leg MFE (ATR from leg):',sorted(round(legs[o['pos_id']][0]['mfe_atr'],2) for o in fail))
print('--- halves')
for nm,f in (('Jan-May',lambda d:d<'2026.06'),('Jun-Nov',lambda d:d>='2026.06')):
    for t in [0.75,0.0]:
        print(nm,t,ev([(end(o),gtp(o,t)) for o in orig if f(o['open_time'])]+[u for u in b1u if f(u[0])]))
print('--- monthly delta t=0 vs 0.75')
c=collections.defaultdict(float)
for o in orig: c[o['open_time'][:7]]+=gtp(o,0.0)-gtp(o,0.75)
print({k[5:]:round(v) for k,v in sorted(c.items())})
