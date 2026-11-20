import sys, collections, datetime as dt
sys.path.insert(0,'/home/user/bob_sim_bot')
from sim.data import load_mt5_csv
from sim.hiwin_sim import Sim
U='/root/.claude/uploads/b0ad39c9-cd6d-5e6e-b914-16374d2871ce/'
m=load_mt5_csv(U+'512dcc18-XAUUSD_M5_202506250345_202611200100.csv')
def stats(tr,lo='2025.07',hi='2026.12'):
    f=lambda t:dt.datetime.utcfromtimestamp(t).strftime('%Y.%m')
    L=sorted([x for x in tr if lo<=f(x.t_open)<hi],key=lambda x:x.t_close)
    eq=pk=dd=0
    for x in L: eq+=x.net/x.lots*0.01; pk=max(pk,eq); dd=max(dd,pk-eq)
    gw=sum(x.net/x.lots for x in L if x.net>0); gl=-sum(x.net/x.lots for x in L if x.net<0)
    return f"n={len(L):4d} net={eq:6.0f} DD={dd:4.0f} RF={eq/max(dd,1):5.2f} PF={gw/max(gl,1e-9):4.2f}"
runs=eval(sys.argv[1])
for name,ov in runs:
    tr=Sim(m,dict(fixed_lot=0.01,**ov)).run()
    print(f'{name:28s} 25H2 {stats(tr,"2025.07","2026.01")} | 2026 {stats(tr,"2026.01","2026.12")} | ALL {stats(tr)}')
