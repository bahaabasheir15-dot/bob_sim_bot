"""MT5-equivalent indicators (same formulas as the stock MQL5 indicator sources)."""
import numpy as np


def ema(x, n):
    a = 2.0 / (n + 1)
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out


def sma(x, n):
    c = np.cumsum(np.insert(x, 0, 0.0))
    out = np.full(len(x), np.nan)
    out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def atr(h, l, c, n=14):
    """MT5 ATR.mq5: simple average of true range."""
    pc = np.concatenate(([c[0]], c[:-1]))
    tr = np.maximum(h, pc) - np.minimum(l, pc)
    tr[0] = h[0] - l[0]
    return sma(tr, n)


def adx(h, l, c, n=14):
    """MT5 ADX.mq5: +DI/-DI/DX smoothed with an EMA of `n`."""
    ph = np.concatenate(([h[0]], h[:-1]))
    pl = np.concatenate(([l[0]], l[:-1]))
    pc = np.concatenate(([c[0]], c[:-1]))
    pdm = np.maximum(h - ph, 0.0)
    ndm = np.maximum(pl - l, 0.0)
    eq = pdm == ndm
    pdm[eq] = 0.0
    ndm[eq] = 0.0
    small = pdm < ndm
    pdm[small] = 0.0
    ndm[~small & ~eq] = 0.0
    tr = np.maximum(h, pc) - np.minimum(l, pc)
    with np.errstate(divide='ignore', invalid='ignore'):
        pdi = np.where(tr != 0, 100.0 * pdm / tr, 0.0)
        ndi = np.where(tr != 0, 100.0 * ndm / tr, 0.0)
    p = ema(pdi, n)
    m = ema(ndi, n)
    with np.errstate(divide='ignore', invalid='ignore'):
        dx = np.where(p + m != 0, 100.0 * np.abs(p - m) / (p + m), 0.0)
    return ema(dx, n)


def bands(c, n=20, k=2.0):
    m = sma(c, n)
    out_u = np.full(len(c), np.nan)
    out_l = np.full(len(c), np.nan)
    w = np.lib.stride_tricks.sliding_window_view(c, n)
    sd = w.std(axis=1)                  # population std, like MT5 StdDev in BB.mq5
    out_u[n - 1:] = m[n - 1:] + k * sd
    out_l[n - 1:] = m[n - 1:] - k * sd
    return out_u, out_l


def rolling_max(x, n):
    out = np.full(len(x), np.nan)
    out[n - 1:] = np.lib.stride_tricks.sliding_window_view(x, n).max(axis=1)
    return out


def rolling_min(x, n):
    out = np.full(len(x), np.nan)
    out[n - 1:] = np.lib.stride_tricks.sliding_window_view(x, n).min(axis=1)
    return out


def ichimoku_spans(h, l, t=9, k=26, s=52):
    """Senkou span A / B as stored in the indicator buffers (CopyBuffer ignores the plot shift)."""
    tenkan = (rolling_max(h, t) + rolling_min(l, t)) / 2
    kijun = (rolling_max(h, k) + rolling_min(l, k)) / 2
    a = (tenkan + kijun) / 2
    b = (rolling_max(h, s) + rolling_min(l, s)) / 2
    return a, b


def rsi(c, n=14):
    """MT5 RSI.mq5: Wilder smoothing, first value = simple average."""
    d = np.diff(c, prepend=c[0])
    up = np.maximum(d, 0.0)
    dn = np.maximum(-d, 0.0)
    out = np.full(len(c), 50.0)
    if len(c) <= n:
        return out
    au = up[1:n + 1].mean()
    ad = dn[1:n + 1].mean()
    for i in range(n + 1, len(c)):
        au = (au * (n - 1) + up[i]) / n
        ad = (ad * (n - 1) + dn[i]) / n
        out[i] = 100.0 if ad == 0 else 100.0 - 100.0 / (1.0 + au / ad)
    return out
