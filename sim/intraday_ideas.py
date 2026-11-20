"""Section 30 of the research log: M5 trend pullback + RSI reset, Z-score mean reversion, FVG retest.
Run from the repo root: python3 sim/intraday_ideas.py "[(name, fn, kwargs), ...]" (fixed 0.01 lot)."""
import sys, numpy as np, datetime as dt, multiprocessing as mp
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
from sim import engines as E, indicators as ind
from sim.data import load_npz, resample
M=load_npz('data/xauusd_plus_m1_2023_2026.npz')
B5=resample(M,5); H=(B5['t']//3600)%24
H1=resample(M,60); e50=ind.ema(H1['c'],50); e200=ind.ema(H1['c'],200)
# H1 trend known at each M5 bar = last CLOSED H1 bar
idx=np.searchsorted(H1['t'],B5['t'],side='right')-2
htr=np.where(idx>=200,np.sign(e50[np.maximum(idx,0)]-e200[np.maximum(idx,0)]),0)

def pullback(tf=5,rsi_n=5,lo=30,hi=70,reset=50,ema_n=50,sl=2.0,tp=2.0,h0=8,h1=20,use_h1=True,maxb=48):
    b=B5 if tf==5 else resample(M,tf); c=b['c']; h=(b['t']//3600)%24
    a=ind.atr(b['h'],b['l'],c,14); r=ind.rsi(c,rsi_n); e=ind.ema(c,ema_n)
    tr=htr if tf==5 else None
    def sig(bb,i):
        if not(h0<=h[i]<h1) or not a[i]>0: return 0
        up = (tr[i]>0) if use_h1 else (c[i]>e[i] and e[i]>e[i-12])
        dn = (tr[i]<0) if use_h1 else (c[i]<e[i] and e[i]<e[i-12])
        dip=min(r[i-4:i])
        if up and c[i]>e[i] and dip<lo and r[i]>reset: return 1
        if dn and c[i]<e[i] and max(r[i-4:i])>hi and r[i]<100-reset: return -1
        return 0
    return E.run_engine(M,tf,sig,dict(sl=lambda bb,i:sl*a[i],tp=lambda bb,i:tp*a[i],max_bars=maxb),name='PB')

def zscore(n=20,z=2.0,adx_max=20,sl_z=1.5,h0=8,h1=20,tf=5,exit_z=0.0,maxb=24):
    b=B5 if tf==5 else resample(M,tf); c=b['c']; h=(b['t']//3600)%24
    m=ind.sma(c,n); w=np.lib.stride_tricks.sliding_window_view(c,n).std(axis=1); sd=np.full(len(c),np.nan); sd[n-1:]=w
    ad=ind.adx(b['h'],b['l'],c,14); Z=(c-m)/np.where(sd>0,sd,np.nan)
    def sig(bb,i):
        if not(h0<=h[i]<h1) or not sd[i]>0 or ad[i]>adx_max: return 0
        if Z[i-1]<=-z and Z[i]>-z: return 1          # re-entry back inside the band
        if Z[i-1]>=z and Z[i]<z: return -1
        return 0
    return E.run_engine(M,tf,sig,dict(sl=lambda bb,i:sl_z*sd[i]+ (z-abs(Z[i]))*sd[i] if False else (abs(Z[i])+sl_z)*sd[i],
                      tp=lambda bb,i:max((abs(Z[i])-exit_z)*sd[i],0.3),max_bars=maxb),name='Z')

def fvg(tf=5,disp=1.0,wait=12,rr=2.0,h0=8,h1=20,trend=True,buf=0.1,minsz=0.2):
    b=B5 if tf==5 else resample(M,tf); o,hh,ll,c=b['o'],b['h'],b['l'],b['c']; h=(b['t']//3600)%24
    a=ind.atr(hh,ll,c,14); gaps=[]; st={}
    tr=htr if tf==5 else np.zeros(len(c))
    def sig(bb,i):
        nonlocal gaps
        # new gap formed at bar i (between i-2 and i, displacement candle i-1)
        if a[i]>0:
            if ll[i]>hh[i-2] and c[i-1]-o[i-1]>disp*a[i] and ll[i]-hh[i-2]>minsz*a[i]: gaps.append((i,1,hh[i-2],ll[i]))
            if hh[i]<ll[i-2] and o[i-1]-c[i-1]>disp*a[i] and ll[i-2]-hh[i]>minsz*a[i]: gaps.append((i,-1,hh[i],ll[i-2]))
        gaps=[g for g in gaps if i-g[0]<=wait]
        if not(h0<=h[i]<h1): return 0
        for g in list(gaps):
            k,d,bot,top=g
            if k==i: continue
            if trend and tr[i]!=d: continue
            if d==1:
                if ll[i]<bot: gaps.remove(g); continue        # gap filled through -> invalid
                if ll[i]<=top and c[i]>top:
                    gaps.remove(g); st[i]=c[i]-(bot-buf*a[i]); return 1
            else:
                if hh[i]>top: gaps.remove(g); continue
                if hh[i]>=bot and c[i]<bot:
                    gaps.remove(g); st[i]=(top+buf*a[i])-c[i]; return -1
        return 0
    return E.run_engine(M,tf,sig,dict(sl=lambda bb,i:max(st[i],0.3),tp=lambda bb,i:rr*max(st[i],0.3),max_bars=48),name='FVG')

def rep(n,tr):
    out=[]
    for Y in ['2023','2024','2025','2026']:
        v=[x['net'] for x in tr if dt.datetime.utcfromtimestamp(x['t_open']).year==int(Y)]; out.append(f"{Y}:{sum(v):6.0f}")
    v=np.array([x['net'] for x in tr]) if tr else np.array([0.0]); pf=v[v>0].sum()/max(-v[v<0].sum(),1e-9)
    return f"{n:30s} "+' '.join(out)+f" | ALL {v.sum():6.0f} PF{pf:4.2f} n{len(tr)} win{(v>0).mean()*100:.0f}%"
def job(a):
    n,f,kw=a; return rep(n,globals()[f](**kw))
if __name__=='__main__':
    with mp.Pool(4) as p:
        for r in p.imap(job,eval(sys.argv[1])): print(r,flush=True)
