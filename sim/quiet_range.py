"""Q1 quiet-day range reversion (user's spec), fixed 0.01 lot, M1-path managed."""
import sys, numpy as np, datetime as dt, multiprocessing as mp
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
from sim.data import load_npz, resample
from sim import indicators as ind
M=load_npz('data/xauusd_plus_m1_2023_2026.npz')
T=M['t']; bh,bl,bc,ah,al,ac,bo,ao=M['bh'],M['bl'],M['bc'],M['ah'],M['al'],M['ac'],M['bo'],M['ao']
b=resample(M,5); o,h,l,c,t=b['o'],b['h'],b['l'],b['c'],b['t']; first=b['first']
a=ind.atr(h,l,c,14); adx=ind.adx(h,l,c,14)
H1=resample(M,60); ha=ind.atr(H1['h'],H1['l'],H1['c'],14); hpct=ha/H1['c']*100
havg=ind.sma(np.nan_to_num(ha),100)
hix=np.searchsorted(H1['t'],t,side='right')-2
cs=np.cumsum(np.insert(np.nan_to_num(a),0,0)); 
HR=(t//3600)%24; DOW=np.array([dt.datetime.utcfromtimestamp(int(x)).weekday() for x in t])
def run(vol_pct=0.12,vol_rel=0.0,n=36,rmin=2.0,rmax=5.0,touch=0.1,adx_max=22,sl_k=0.6,tp_frac=0.65,be_at=0.6,h0=9,h1=20,close_h=21,spike=1.5,need_mid=True,use_be=True):
    out=[]; i=60
    nb=len(t)
    while i<nb-2:
        if not(h0<=HR[i]<h1) or (DOW[i]==4 and HR[i]>=20) or not a[i]>0 or hix[i]<100: i+=1; continue
        if vol_pct>0 and not hpct[hix[i]]<vol_pct: i+=1; continue
        if vol_rel>0 and not ha[hix[i]]<vol_rel*havg[hix[i]]: i+=1; continue
        if spike>0 and a[i]>spike*(cs[i]-cs[i-50])/50: i+=1; continue
        if adx[i]>=adx_max: i+=1; continue
        RH=h[i-n:i].max(); RL=l[i-n:i].min(); R=RH-RL      # range = 36 bars before the signal candle i
        if not(rmin*a[i]<=R<=rmax*a[i]): i+=1; continue
        j=first[i+1]; sp=ao[j]-bo[j]
        if 0.5*R<4*(0.06+sp): i+=1; continue
        mid=(h[i]+l[i])/2; d=0
        if h[i]>=RH-touch*a[i] and c[i]<RH and (c[i]<mid or not need_mid): d=-1
        elif l[i]<=RL+touch*a[i] and c[i]>RL and (c[i]>mid or not need_mid): d=1
        if d==0: i+=1; continue
        op=ao[j] if d==1 else bo[j]
        sl=(RL-sl_k*a[i]) if d==1 else (RH+sl_k*a[i])
        rm=(RH+RL)/2; tpd=min(abs(rm-op),tp_frac*R) if (rm-op)*d>0 else tp_frac*R
        tp=op+d*tpd; bel=op+d*be_at*tpd; moved=False
        if (sl-op)*d>=0: i+=1; continue
        cp=None; k=j
        while k<len(T):
            if (T[k]//3600)%24>=close_h or T[k]//86400!=T[j]//86400:
                cp=bc[k] if d==1 else ac[k]; break
            lo=bl[k] if d==1 else al[k]; hi=bh[k] if d==1 else ah[k]
            adv=lo if d==1 else hi; fav=hi if d==1 else lo
            if (adv-sl)*d<=0: cp=sl; break
            if (fav-tp)*d>=0: cp=tp; break
            if use_be and not moved and (fav-bel)*d>=0:
                sl=op+d*0.06; moved=True
            k+=1
        if cp is None: break
        out.append((T[j],d*(cp-op)-0.06))
        # continue after exit
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
