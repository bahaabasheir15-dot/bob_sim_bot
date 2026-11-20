"""Load Dukascopy M1 bid/ask candles and convert them to broker server time.

Server time of Vantage (and most MT5 brokers): UTC+2, UTC+3 while US daylight
saving is on (2nd Sunday of March -> 1st Sunday of November), so that the
daily candle closes at 17:00 New York.
"""
import datetime as dt
import lzma
import os
import struct

import numpy as np

DIV = 1000.0   # XAUUSD price scale in Dukascopy files


def _us_dst(d):
    y = d.year
    mar = dt.date(y, 3, 8 + (6 - dt.date(y, 3, 8).weekday()) % 7)    # 2nd Sunday of March
    nov = dt.date(y, 11, 1 + (6 - dt.date(y, 11, 1).weekday()) % 7)  # 1st Sunday of November
    return mar <= d < nov


def server_offset(d):
    return 3 if _us_dst(d) else 2


def _read(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    raw = lzma.decompress(open(path, 'rb').read())
    n = len(raw) // 24
    a = np.frombuffer(raw, dtype='>i4,>i4,>i4,>i4,>i4,>f4', count=n)
    return a


def load(root, start, end):
    """Return dict of numpy arrays, one row per traded minute, times in server time (epoch seconds)."""
    d = dt.date.fromisoformat(start)
    e = dt.date.fromisoformat(end)
    cols = {k: [] for k in ('t', 'bo', 'bh', 'bl', 'bc', 'ao', 'ah', 'al', 'ac')}
    while d <= e:
        base = os.path.join(root, f'{d.year}', f'{d.month:02d}', f'{d.day:02d}')
        b = _read(base + '_BID.bi5')
        a = _read(base + '_ASK.bi5')
        if b is not None and a is not None and len(b) == len(a):
            vol = b['f5'] + a['f5']
            keep = vol > 0                     # no ticks in that minute -> MT5 has no bar either
            if keep.any():
                t0 = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())
                t = t0 + b['f0'][keep].astype(np.int64)
                # offset decided per minute (DST switches happen on Sunday, no trading then)
                off = server_offset(d) * 3600
                cols['t'].append(t + off)
                for k, arr, f in (('bo', b, 'f1'), ('bc', b, 'f2'), ('bl', b, 'f3'), ('bh', b, 'f4'),
                                  ('ao', a, 'f1'), ('ac', a, 'f2'), ('al', a, 'f3'), ('ah', a, 'f4')):
                    cols[k].append(arr[f][keep] / DIV)
        d += dt.timedelta(days=1)
    out = {k: np.concatenate(v) for k, v in cols.items()}
    order = np.argsort(out['t'], kind='stable')
    return {k: v[order] for k, v in out.items()}


def resample(m1, minutes):
    """Bid OHLC bars of `minutes` length from M1 (server time). Returns dict with t (bar open), o,h,l,c."""
    key = m1['t'] // (minutes * 60)
    idx = np.flatnonzero(np.diff(key)) + 1
    starts = np.concatenate(([0], idx))
    ends = np.concatenate((idx, [len(key)]))
    return dict(t=key[starts] * minutes * 60,
                o=m1['bo'][starts],
                h=np.maximum.reduceat(m1['bh'], starts),
                l=np.minimum.reduceat(m1['bl'], starts),
                c=m1['bc'][ends - 1],
                first=starts, last=ends - 1)


def load_mt5_csv(path, point=0.01):
    """M1 bars exported from MT5 (View > Symbols > Bars > Export). Tab separated:
    <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>. Times are already
    broker server time; ask = bid + spread (points)."""
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8', 'replace')
    t, o, h, l, c, sp = [], [], [], [], [], []
    for line in text.splitlines():
        f = line.replace(',', '\t').split('\t') if '\t' in line or line.count(',') >= 6 else line.split()
        if len(f) < 9 or not f[0][:1].isdigit():
            continue
        d = dt.datetime.strptime(f[0] + ' ' + f[1][:8], '%Y.%m.%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
        t.append(int(d.timestamp()))
        o.append(float(f[2])); h.append(float(f[3])); l.append(float(f[4])); c.append(float(f[5]))
        sp.append(float(f[8]) * point)
    t = np.array(t, dtype=np.int64)
    o, h, l, c, sp = (np.array(x) for x in (o, h, l, c, sp))
    return dict(t=t, bo=o, bh=h, bl=l, bc=c, ao=o + sp, ah=h + sp, al=l + sp, ac=c + sp)


def load_npz(path):
    """Load M1 data saved by this project: either the full float format, or the compact repo file
    data/xauusd_plus_m1_2023_2026.npz (prices in cents as int32, one bar spread `sp` in cents)."""
    z = np.load(path)
    if 'sp' not in z.files:
        return {k: z[k] for k in z.files}
    sp = z['sp'].astype(np.float64) / 100.0
    out = {'t': z['t'].astype(np.int64)}
    for k in ('bo', 'bh', 'bl', 'bc'):
        out[k] = z[k].astype(np.float64) / 100.0
    out['ao'], out['ah'], out['al'], out['ac'] = out['bo'] + sp, out['bh'] + sp, out['bl'] + sp, out['bc'] + sp
    return out
