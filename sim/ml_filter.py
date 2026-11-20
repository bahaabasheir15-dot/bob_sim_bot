#!/usr/bin/env python3
"""Machine-learning trade filter (meta-labelling), tested walk-forward.

The engines still find the trades; the model only decides which ones to SKIP.
It is always trained on earlier years and judged on a later year it never saw:
    train 2024        -> test 2025
    train 2024 + 2025 -> test 2026

    python3 -m sim.ml_filter m1.npz L1        (or S for the scalper originals)
"""
import datetime as dt
import sys

import numpy as np

from . import indicators as ind
from .data import resample
from .hiwin_sim import Sim

V44 = dict(use_b1=False, atr_hard_min_pct=0.14, recover_tp_atr=0.0, use_ldn=True, use_s4=True,
           use_trend=True, tr_risk_pct=0.25, ldn_sl_mult=1.75, sl_atr=7.0, fixed_lot=0.01)


class Features:
    """Market state known at the moment a trade is opened (closed candles only)."""

    def __init__(self, m1):
        self.h1 = h1 = resample(m1, 60)
        self.d1 = d1 = resample(m1, 1440)
        self.m5 = m5 = resample(m1, 5)
        c = h1['c']
        self.h1_e20 = ind.ema(c, 20)
        self.h1_e50 = ind.ema(c, 50)
        self.h1_e200 = ind.ema(c, 200)
        self.h1_rsi = ind.rsi(c, 14)
        self.h1_atr = ind.atr(h1['h'], h1['l'], c, 14)
        self.h1_adx = ind.adx(h1['h'], h1['l'], c, 14)
        self.d1_atr = ind.atr(d1['h'], d1['l'], d1['c'], 14)
        self.m5_atr = ind.atr(m5['h'], m5['l'], m5['c'], 14)
        self.m5_rsi = ind.rsi(m5['c'], 14)
        self.m5_adx = ind.adx(m5['h'], m5['l'], m5['c'], 14)

    def at(self, t, buy, unit):
        d = 1 if buy else -1
        h1, d1, m5 = self.h1, self.d1, self.m5
        i = np.searchsorted(h1['t'], t, side='right') - 2      # last closed H1
        j = np.searchsorted(d1['t'], t, side='right') - 2      # yesterday
        k = np.searchsorted(m5['t'], t, side='right') - 2      # last closed M5
        c = h1['c'][i]
        a = self.h1_atr[i] or 1e-9
        da = self.d1_atr[j] or 1e-9
        dt_ = dt.datetime.utcfromtimestamp(int(t))
        # atr percentile of the last 20 days of H1
        hist = self.h1_atr[max(0, i - 480):i + 1]
        pct = float((hist < self.h1_atr[i]).mean()) if len(hist) > 10 else 0.5
        y_rng = d1['h'][j] - d1['l'][j]
        return [
            unit / c * 100,                                   # stop unit as % of price
            unit / da,                                        # stop unit vs daily ATR
            d * (c - self.h1_e20[i]) / a,                     # distance to H1 EMA20, signed by direction
            d * (c - self.h1_e50[i]) / a,
            d * np.sign(self.h1_e50[i] - self.h1_e200[i]),    # with / against the H1 trend
            self.h1_rsi[i] if buy else 100 - self.h1_rsi[i],
            self.h1_adx[i],
            pct,                                              # how volatile vs the last 20 days
            a / c * 100,
            y_rng / da,                                       # yesterday's range vs normal
            d * (d1['c'][j] - d1['o'][j]) / da,               # yesterday's candle, signed
            d * (c - d1['c'][j]) / da,                        # move since yesterday's close
            self.m5_rsi[k] if buy else 100 - self.m5_rsi[k],
            self.m5_adx[k],
            self.m5_atr[k] / a,
            dt_.hour + dt_.minute / 60.0,
            dt_.weekday(),
        ]


def dataset(m1, tag):
    tr = Sim(m1, V44).run()
    F = Features(m1)
    if tag == 'S':
        legs = {x.parent: x for x in tr if x.tag == 'R'}
        sel = [x for x in tr if x.tag in ('S1', 'S4', 'S5')]
        net = [x.net + (legs[x.id].net if x.id in legs else 0.0) for x in sel]     # whole rescue group
    else:
        sel = [x for x in tr if x.tag == tag]
        net = [x.net for x in sel]
    X = np.array([F.at(x.t_open, x.buy, x.atr_e) for x in sel], dtype=float)
    yr = np.array([dt.datetime.utcfromtimestamp(x.t_open).year for x in sel])
    return X, np.array(net), yr


def pf(n):
    gw = n[n > 0].sum()
    gl = -n[n < 0].sum()
    return gw / gl if gl else 99.0


def evaluate(X, net, yr, make_model, keep_frac):
    """Train on earlier years, skip the (1-keep_frac) of test trades the model likes least."""
    out = []
    for train_years, test_year in (((2024,), 2025), ((2024, 2025), 2026)):
        tr = np.isin(yr, train_years)
        te = yr == test_year
        m = make_model()
        m.fit(X[tr], (net[tr] > 0).astype(int))
        p = m.predict_proba(X[te])[:, 1]
        thr = np.quantile(m.predict_proba(X[tr])[:, 1], 1 - keep_frac)   # threshold set on TRAIN data only
        keep = p >= thr
        out.append((test_year, net[te].sum(), pf(net[te]), te.sum(), net[te][keep].sum(), pf(net[te][keep]), keep.sum()))
    return out


def main(data, tag):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    z = np.load(data)
    m1 = {k: z[k] for k in z.files}
    X, net, yr = dataset(m1, tag)
    X = np.nan_to_num(X)
    print(f'{tag}: {len(net)} trades, by year', {y: int((yr == y).sum()) for y in (2024, 2025, 2026)})
    models = {
        'logistic': lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=2000)),
        'boosting': lambda: HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=150,
                                                           min_samples_leaf=40, l2_regularization=1.0),
    }
    for name, mk in models.items():
        for keep in (0.9, 0.8, 0.7, 0.6):
            res = evaluate(X, net, yr, mk, keep)
            cells = ' | '.join(f'{y}: all {a:6.0f} PF{b:4.2f} n{c} -> kept {d:6.0f} PF{e:4.2f} n{f}'
                               for y, a, b, c, d, e, f in res)
            print(f'  {name:8s} keep {keep:.0%}: {cells}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
