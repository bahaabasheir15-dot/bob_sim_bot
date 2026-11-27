# Track C — higher win rate WITHOUT lower profit
Status: TODO / IN PROGRESS (time) / ACCEPTED / REJECTED (reason). Measure BOTH: trade win % and basket win %
(scalp original + its R leg = one basket). Known: smaller targets alone raise win % but cut profit (log 74).
Current: trade 74.6%, basket 80.9%; L1 59%, X1 69%, N1 81%, scalper 82%.

1. REJECTED (2026-11-27: win 77.5% but net 11,469 < 12,063) — London partial target: close half at 0.5 range, move stop to entry, rest to 1 range.
2. TODO — X1 partial: close half at +1.0% (and +0.7%), rest to 3% with break-even.
3. TODO — Night engine fixed target +0.3% / +0.4% (exit early when reached, else normal exit).
4. TODO — Scalper split: half at 0.3 ATR, half at 0.5 ATR.
5. TODO — London: skip breakouts whose 5-min breakout candle closed in the lower/upper third (weak close) — win % and net.
6. TODO — X1: skip breakouts when price already ran > 1.5 daily ATR today (late breakouts fail more).
7. TODO — Scalper S6: require the fade candle body > 50% of its range.
