"""A1 hybrid (Gemini proposal): mode F = ER squeeze -> flow breakout; mode Q = quiet range / velocity fade with tight stop."""
import sys, numpy as np, datetime as dt, multiprocessing as mp
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
from sim.data import load_npz, resample
from sim import indicators as ind
M=load_npz('data/xauusd_plus_m1_2023_2026.npz')
T=M['t']; bh,bl,bc,ah,al,ac,bo,ao=M['bh'],M['bl'],M['bc'],M['ah'],M['al'],M['ac'],M['bo'],M['ao']
b=resample(M,5); o,h,l,c,t=b['o'],b['h'],b['l'],b['c'],b['t']; first=b['first']
a=ind.atr(h,l,c,14)
m15=resample(M,15); e15=ind.ema(m15['c'],50); i15=np.searchsorted(m15['t'],t,side='right')-2
d1=resample(M,1440); da=ind.atr(d1['h'],d1['l'],d1['c'],14); id1=np.searchsorted(d1['t'],t,side='right')-2
dd=np.abs(np.diff(c,prepend=c[0])); cs=np.cumsum(dd)
ER=np.full(len(c),np.nan); ER[12:]=np.abs(c[12:]-c[:-12])/np.maximum(cs[12:]-cs[:-12],1e-9)
HR=(t//3600)%24; DOW=np.array([dt.datetime.utcfromtimestamp(int(x)).weekday() for x in t])
def manage(j,d,op,sl,tp,be_r,trail,close_h=21):
    R=abs(op-sl); k=j; best=op; on=False
    while k<len(T):
        if (T[k]//3600)%24>=close_h or T[k]//86400!=T[j]//86400:
            return (bc[k] if d==1 else ac[k]),k
        lo=bl[k] if d==1 else al[k]; hi=bh[k] if d==1 else ah[k]
        adv=lo if d==1 else hi; fav=hi if d==1 else lo
        if (adv-sl)*d<=0: return sl,k
        if tp is not None and (fav-tp)*d>=0: return tp,k
        best=max(best,fav) if d==1 else min(best,fav)
        if be_r and (best-op)*d>=be_r*R:
            ns=op+d*0.06
            if (ns-sl)*d>0: sl=ns
            on=True
        if trail and on:
            ns=best-d*trail
            if (ns-sl)*d>0: sl=ns
        k+=1
    return None,k
def run(mode='F',er_lo=0.25,er_hi=0.48,body=1.2,sl_k=1.2,be_r=1.0,trail=0.8,ema=True,
        q_dpct=0.9,q_er=0.28,q_n=30,vel=2.2,q_sl=0.7,q_rr=1.1,h0=8,h1=20,maxday=3):
    out=[]; i=60; nb=len(t); day=None; cnt=0; consec=0
    while i<nb-2:
        if t[i]//86400!=day: day=t[i]//86400; cnt=0; consec=0
        if not(h0<=HR[i]<h1) or (DOW[i]==4 and HR[i]>=20) or not a[i]>0 or cnt>=maxday or consec>=2 or np.isnan(ER[i-8]): i+=1; continue
        j=first[i+1]; sp=ao[j]-bo[j]; d=0
        if mode=='F':
            if np.nanmin(ER[i-8:i])<er_lo and ER[i]>er_hi:
                if c[i]-o[i]>=body*a[i] and h[i]>h[i-12:i].max() and (not ema or c[i]>e15[i15[i]]): d=1
                elif o[i]-c[i]>=body*a[i] and l[i]<l[i-12:i].min() and (not ema or c[i]<e15[i15[i]]): d=-1
            if d:
                op=ao[j] if d==1 else bo[j]; sl=op-d*sl_k*a[i]; tp=None; br,tr=be_r,trail*a[i]
        else:
            if not(id1[i]>14 and da[id1[i]]/c[i]*100<q_dpct and ER[i]<q_er): i+=1; continue
            RH=h[i-q_n:i].max(); RL=l[i-q_n:i].min(); mid=(h[i]+l[i])/2; v=(c[i]-c[i-3])/a[i]
            if (h[i]>=RH or v>=vel) and c[i]<mid: d=-1
            elif (l[i]<=RL or v<=-vel) and c[i]>mid: d=1
            if d:
                op=ao[j] if d==1 else bo[j]
                sl=(l[i]-q_sl*a[i]) if d==1 else (h[i]+q_sl*a[i]); R=abs(op-sl)
                if (op-sl)*d<=0: i+=1; continue
                rm=(RH+RL)/2; dist=min(abs(rm-op) if (rm-op)*d>0 else 1e9, q_rr*R)
                if dist<3.5*(0.06+sp): i+=1; continue
                tp=op+d*dist; br,tr=0,0
        if not d: i+=1; continue
        cp,k=manage(j,d,op,sl,tp,br,tr)
        if cp is None: break
        pnl=d*(cp-op)-0.06; out.append((T[j],pnl)); cnt+=1; consec=consec+1 if pnl<0 else 0
        i=max(i+1,np.searchsorted(t,T[k],side='right'))
    return out
def rep(nm,o):
    s=[]
    for Y in (2023,2024,2025,2026):
        v=[x for tt,x in o if dt.datetime.utcfromtimestamp(tt).year==Y]; s.append(f"{Y}:{sum(v):6.0f}/{len(v):4d}")
    v=np.array([x for _,x in o]) if o else np.zeros(1); pf=v[v>0].sum()/max(-v[v<0].sum(),1e-9)
    return f"{nm:30s} "+' '.join(s)+f" | ALL {v.sum():6.0f} PF{pf:4.2f} win{(v>0).mean()*100:.0f}%"
def job(x): nm,kw=x; return rep(nm,run(**kw))
if __name__=='__main__':
    with mp.Pool(4) as p:
        for r in p.imap(job,eval(sys.argv[1])): print(r,flush=True)
