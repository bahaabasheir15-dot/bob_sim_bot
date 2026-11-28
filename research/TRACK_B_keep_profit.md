# Track B — keep the profit (lower drawdown, worst month, calm years)
Status: TODO / IN PROGRESS (time) / ACCEPTED / REJECTED (reason). Already rejected: drawdown throttle, monthly stop,
volatility-regime model, ML trade filter, profit-lock floor (cut 2025/26), allocation by inverse vol / momentum (log 77).

1. REJECTED (2026-11-27: every year lower, $5k 1.48M -> 1.10M; $2k DD 23.2%) — Volatility-target lot: scale every engine's lot by (median daily ATR% of last 60 days / today's daily ATR%), clipped 0.7-1.3.
2. IN PROGRESS (2026-11-28T00:44Z) — News blackout: no new scalps 15:00-17:00 server on the first Friday of each month (NFP) and on US CPI days (2nd week Wed/Thu heuristic); check every year.
3. TODO — Weekly profit keep: after the week is >= +X% (X = 4/6/8), next scalps that week at 0.5x lot.
4. TODO — Scalper daily loss stop per engine: after 2 stopped scalp baskets in one day, no more scalps that day.
5. TODO — X1 only when the 120-H4 channel width is between 3% and 12% (calm 2023 channels too narrow?) — re-check with account runs.
6. TODO — Friday: close all scalp baskets at 20:00 server Friday (no weekend gap risk) — check every year.
7. TODO — Equity-curve filter per engine: trade an engine at 0.5x when its own 20-trade equity curve is below its 50-trade average.
