# Research queue (one idea per run, top to bottom)

Status: TODO / IN PROGRESS (run time) / ACCEPTED / REJECTED (reason)

1. TODO — London engine: trade only after a day that moved >= X% (the filter that worked for the night engine).
2. TODO — Scalper: same previous-day-move filter (skip or halve lot after quiet days).
3. TODO — Night engine: exit time 03:00 / 03:30 / 04:30 / 05:00 with the 1% filter on.
4. TODO — Night engine: entry 01:15 / 01:30 instead of 01:05.
5. TODO — Night engine: stop based on ATR (H1 or D1) instead of 0.5% of price.
6. TODO — Night engine: skip Fridays (week-end positioning) — check every year.
7. TODO — Night engine short side: SELL at night after a big UP day, as a test of symmetry (expect reject).
8. TODO — London engine: minimum / maximum range width relative to the daily ATR.
9. TODO — London engine: skip days with major US data (first Friday of the month 15:30 server = NFP).
10. TODO — Trend engine: n = 80 / 100 / 120 checked with account runs on $5,000 and $1,000.
11. TODO — Trend engine: only trade when the daily ATR is expanding (today's ATR > 20-day average).
12. TODO — Scalper: ATR floor 0.13% / 0.15% re-checked on 4 years with account runs.
13. TODO — Scalper: max 3 open originals with the 7 ATR stop (was mixed on 3 years).
14. TODO — Turn-of-month effect: does any engine do better/worse in the first/last 2 trading days of a month?
15. TODO — Equal-risk weighting: scale each engine's lot so each contributes the same risk; compare DD.
16. TODO — Weekday effect per engine (accept only if the same weekday is weak in all 4 years).
