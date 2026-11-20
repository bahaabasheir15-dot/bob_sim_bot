import sys, time, collections, datetime as dt
sys.path.insert(0,'/home/user/bob_sim_bot')
from sim.data import load_mt5_csv
from sim.hiwin_sim import Sim
U='/root/.claude/uploads/b0ad39c9-cd6d-5e6e-b914-16374d2871ce/'
src=sys.argv[1]; over=eval(sys.argv[2]) if len(sys.argv)>2 else {}
m1=load_mt5_csv(U+src)
t0=time.time(); s=Sim(m1,over); tr=s.run(); print('run',round(time.time()-t0),'s, bars',len(m1['t']))
sys.argv=['x']; exec(open('/home/user/bob_sim_bot/analysis/analyze_tester_report.py').read().split("if __name__")[0])
d,o=load(U+'05fa7170-ReportTester-26453869.html'); MT=build_trades(d)
lo,hi='2026.08.17','2026.11.20'
mt=[t for t in MT if lo<=t['tin']<hi and t['kind'] in('S1','S5','B')]
f=lambda t:dt.datetime.utcfromtimestamp(t).strftime('%Y.%m.%d %H:%M:%S')
st=[x for x in tr if lo<=f(x.t_open)<hi and x.tag in('S1','S5','B1')]
P=lambda s:dt.datetime.strptime(s,'%Y.%m.%d %H:%M:%S')
used=set();hit=[]
for t in mt:
    tag='B1' if t['kind']=='B' else t['kind']
    for i,x in enumerate(st):
        if i in used or x.tag!=tag or x.buy!=(t['side']=='buy'): continue
        if abs((P(f(x.t_open))-P(t['tin'])).total_seconds())<=600: used.add(i); hit.append((t,x)); break
print('MT5',collections.Counter(('B1' if t['kind']=='B' else t['kind']) for t in mt),'SIM',collections.Counter(x.tag for x in st))
print('matched',len(hit),f'= {len(hit)/len(mt)*100:.0f}% of MT5, {len(hit)/max(1,len(st))*100:.0f}% of sim')
mt01=sum(t['n01'] for t in MT if lo<=t['tin']<hi); st01=sum(x.net/x.lots*0.01 for x in tr if lo<=f(x.t_open)<hi)
print('net per 0.01  MT5',round(mt01),' SIM',round(st01))
same=sum(1 for t,x in hit if (t['net']>0)==(x.net>0)); print('same win/loss on matched',same,'/',len(hit))
miss=[t for t in mt if not any(t is h[0] for h in hit)][:8]
print('MT5 unmatched sample',[(t['kind'],t['side'],t['tin']) for t in miss])
extra=[x for i,x in enumerate(st) if i not in used][:8]
print('SIM unmatched sample',[(x.tag,'buy' if x.buy else 'sell',f(x.t_open)) for x in extra])
