"""Time-of-day micro-cycle: stats per (slot, prior-move class) learned on PAST data only, then traded."""
import sys, numpy as np, datetime as dt
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
from sim.data import load_npz, resample
from sim import indicators as ind
M=load_npz('data/xauusd_plus_m1_2023_2026.npz')
b=resample(M,5); t=b['t']; o,h,l,c=b['o'],b['h'],b['l'],b['c']
sp=(M['ao']-M['bo'])[b['first']]
a=ind.atr(h,l,c,14)
D=[dt.datetime.utcfromtimestamp(int(x)) for x in t]
yr=np.array([d.year for d in D]); mon=np.array([(d.year-2023)*12+d.month-1 for d in D]); dow=np.array([d.weekday() for d in D])
mod=(t%86400)//60
NIGHT=lambda m:(60<=m<245)
def cand(slot_min,L,H,thr,sl):
    n=len(t); i=np.flatnonzero((mod%slot_min==0)&(a>0)); i=i[(i>L+1)&(i<n-H-1)]
    i=i[(t[i+H]-t[i-L-1])<=(L+H+1)*300+900]
    p=(c[i-1]-c[i-1-L])/a[i-1]
    cls=np.where(p>thr,1,np.where(p<-thr,-1,0))
    key=(mod[i]//slot_min)*3+(cls+1)
    e=o[i]; s=sl*a[i-1]
    lo=np.array([l[x:x+H].min() for x in i]); hi=np.array([h[x:x+H].max() for x in i]); ex=c[i+H-1]
    bp=np.where(lo<=e-s,-s,ex-e); spp=np.where(hi+sp[i]>=e+sp[i]+s,-s,e-ex)  # sell: entry bid e, exit ask
    cost=sp[i]+0.06
    return i,key,bp-cost,spp-cost
def run(slot_min=30,L=6,H=6,thr=1.0,sl=3.0,tmin=2.5,train='expand',min_months=12,no_night=True,minn=40):
    i,key,BP,SP=cand(slot_min,L,H,thr,sl)
    m=mon[i]; trades=[]
    nk=(1440//slot_min)*3
    for M_ in range(0,mon.max()+1):
        if train=='expand':
            if M_<min_months: continue
            tr=m<M_
        else:  # leave-one-year-out (uses future years: stability check only)
            tr=yr[i]!=(2023+M_//12)
        te=np.flatnonzero(m==M_)
        if len(te)==0: continue
        for side,P in ((1,BP),(-1,SP)):
            s=np.bincount(key[tr],P[tr],nk); n=np.bincount(key[tr],None,nk); s2=np.bincount(key[tr],P[tr]**2,nk)
            mu=s/np.maximum(n,1); sd=np.sqrt(np.maximum(s2/np.maximum(n,1)-mu**2,1e-9)); ts=mu/sd*np.sqrt(np.maximum(n,1))
            good=(ts>tmin)&(n>=minn)
            for x in te[good[key[te]]]:
                if no_night and NIGHT(mod[i[x]]): continue
                trades.append((t[i[x]],side,P[x],key[x]))
    # one trade at a time: drop overlaps
    trades.sort(); out=[]; busy=-1
    for tt,sd_,pn,k in trades:
        if tt<busy: continue
        out.append((tt,sd_,pn,k)); busy=tt+H*300
    return out
def rep(name,o):
    s=[]
    for Y in (2023,2024,2025,2026):
        v=[x[2] for x in o if dt.datetime.utcfromtimestamp(x[0]).year==Y]; s.append(f"{Y}:{sum(v):6.0f}/{len(v):4d}")
    v=np.array([x[2] for x in o]) if o else np.zeros(1); pf=v[v>0].sum()/max(-v[v<0].sum(),1e-9)
    print(f"{name:34s} "+' '.join(s)+f" | ALL {v.sum():6.0f} PF{pf:4.2f} win{(v>0).mean()*100:.0f}%",flush=True)
if __name__=='__main__':
    for n,kw in eval(sys.argv[1]): rep(n,run(**kw))
