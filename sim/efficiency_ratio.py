"""Friction -> flow: low Efficiency Ratio over 12 M5 bars, then one wide candle lifts ER sharply -> trade with it."""
import sys, numpy as np, datetime as dt, multiprocessing as mp
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
from sim import engines as E, indicators as ind
from sim.data import load_npz, resample
M=load_npz('data/xauusd_plus_m1_2023_2026.npz')
H1=resample(M,60); e50=ind.ema(H1['c'],50); e200=ind.ema(H1['c'],200)
def er_engine(tf=5,n=12,lo=0.2,hi=0.45,rng_k=1.5,close_pos=0.7,sl_mode='bar',sl_k=1.5,rr=1.5,trail=0.0,h0=8,h1=20,trend=0,maxb=24,wick_k=0.0,fade=False):
    b=resample(M,tf); o,hh,ll,c=b['o'],b['h'],b['l'],b['c']; t=b['t']; H=(t//3600)%24
    a=ind.atr(hh,ll,c,14)
    d=np.abs(np.diff(c,prepend=c[0])); cs=np.cumsum(d)
    ER=np.full(len(c),np.nan); ER[n:]=np.abs(c[n:]-c[:-n])/np.maximum(cs[n:]-cs[:-n],1e-9)
    # wick-to-body over the friction window (optional): average wick share
    body=np.abs(c-o); rg=np.maximum(hh-ll,1e-9); wk=1-body/rg
    wks=np.convolve(wk,np.ones(n)/n)[:len(wk)]
    idx=np.searchsorted(H1['t'],t,side='right')-2; tr=np.sign(e50[np.maximum(idx,0)]-e200[np.maximum(idx,0)])
    st={}
    def sig(bb,i):
        if not(h0<=H[i]<h1) or not a[i]>0 or np.isnan(ER[i-1]): return 0
        if ER[i-1]>lo or ER[i]<hi: return 0
        if wick_k>0 and wks[i-1]<wick_k: return 0
        r=hh[i]-ll[i]
        if r<rng_k*a[i-1]: return 0
        pos=(c[i]-ll[i])/r
        dr=1 if pos>=close_pos else -1 if pos<=1-close_pos else 0
        if dr==0 or (trend and tr[i]!=dr): return 0
        st[i]=(c[i]-ll[i]+0.1*a[i]) if dr==1 else (hh[i]-c[i]+0.1*a[i])
        if sl_mode=='atr' or fade: st[i]=sl_k*a[i]
        return -dr if fade else dr
    man=dict(sl=lambda bb,i:max(st[i],0.3),max_bars=maxb)
    if rr>0: man['tp']=lambda bb,i:rr*max(st[i],0.3)
    if trail>0: man['trail']=lambda bb,i:trail*a[i]
    return E.run_engine(M,tf,sig,man,name='ER')
def rep(n,tr):
    out=[]
    for Y in ['2023','2024','2025','2026']:
        v=[x['net'] for x in tr if dt.datetime.utcfromtimestamp(x['t_open']).year==int(Y)]; out.append(f"{Y}:{sum(v):6.0f}")
    v=np.array([x['net'] for x in tr]) if tr else np.array([0.0]); pf=v[v>0].sum()/max(-v[v<0].sum(),1e-9)
    return f"{n:30s} "+' '.join(out)+f" | ALL {v.sum():6.0f} PF{pf:4.2f} n{len(tr)} win{(v>0).mean()*100:.0f}%"
def job(a): n,kw=a; return rep(n,er_engine(**kw))
if __name__=='__main__':
    with mp.Pool(4) as p:
        for r in p.imap(job,eval(sys.argv[1])): print(r,flush=True)
