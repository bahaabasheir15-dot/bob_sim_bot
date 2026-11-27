# Track A — turn losses into profit
Status: TODO / IN PROGRESS (time) / ACCEPTED / REJECTED (reason). Already rejected (do not repeat): counter-trade
rescue H for every engine, reverse after stop, second-chance London, London recovery leg, London/night/scalp longer
holds beyond v45.7, tighter group stop, harvest (v45.9 is a separate candidate), brain size cut (v45.8 candidate),
rebound sizing after a loss (log 77).

1. REJECTED (2026-11-27: 2024 1,050 vs 1,120; $5k DD 20.5%) — X1 re-arm: after an X1 trade is stopped, keep its level armed for a second break in the same H4 candle window (one retry).
2. TODO — X1 structure stop: stop below the last H4 swing low / above swing high (capped 0.3-0.7%) instead of a fixed 0.45%.
3. TODO — Scalper recovery leg size 1.5x / 2x of the original (recover_lot_mult) with the 7 ATR group stop; group target at the average.
4. TODO — Scalper: recovery leg at 2.5 / 3 ATR instead of 2 ATR (later leg = better average) — check 4 years.
5. TODO — London losing trade at 21:00: close half, keep half with stop at entry until 02:00 (not the full hold already rejected).
6. TODO — Scalp basket stopped -> the NEXT scalp of the same day only in the direction of the move that stopped it.
7. TODO — Night engine: when yesterday's bot day was negative, enter 30 min earlier (01:05 -> 00:35) with the same stop.
