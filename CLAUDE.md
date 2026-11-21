# XAU HiWin — project memory (read this first)

## How to talk to the user
- **Always answer in Egyptian Arabic.** The user does not read English. Keep file names, settings and code in English inside backticks.
- The user runs MT5 tests and demo accounts and sends reports (HTML), screenshots and CSV logs. Be honest about bad results; never oversell.
- Rule we always follow: a change is accepted only if it improves EVERY year on its own (2023, 2024, 2025, 2026) and holds with several nearby settings. Pick the middle of what works, not the best value.

## Current state (2026-11-20)
- **Best version: v45.3** — `ea/XAU_HiWin_EA_v45_3.mq5`, `#property version "45.30"`, magic `20263255` (same as v45.2). = v45.2 + scalper setup `S6` (velocity exhaustion). Older v45.2 = `ea/XAU_HiWin_EA_v45.mq5`; `InpUseS6=false` turns v45.3 back into v45.2.
- Engines (comment tag on each trade): scalper `S1` `S4` `S5` `S6` (M5 pullback / S6 = 4 candles ran >= 2.5 ATR and candle 1 closed back past its middle -> fade; skips ADX/spike/ATR-floor filters, TP 0.5 ATR, SL 7 ATR, limit entry), recovery leg `R` (group closes at average entry), London breakout `L1` (Asian range 03-09 server, SL 1.75 ranges, TP 1 range, close 21:00, half lot), H1 trend `T1` (55-bar break, SL 3 ATR, trail 4 ATR, 0.25% risk, skips if min lot > 1% risk), night drift `N1` (buy 01:05 sell 04:00 server time, only after a day that moved >= 1%, no Mondays, full lot, stop 0.5% of price).
- Tester, Vantage XAUUSD+, 2023.01.01-2026.11.19, real ticks:
  - v45.2 from $1,000: net +44,138, PF 1.68, max DD 27.8% (in 2023, small account = min-lot effect), median month +5.7%, worst month -10.3%. Years: 2023 -7, 2024 +531, 2025 +2,257, 2026 +41,416.
  - v45.1 from $5,000: net +105,486, PF 1.66, max DD 16.7%. Years: 2023 -353, 2024 +1,527, 2025 +7,790, 2026 +96,685.
  - Simulator v45.2 from $5,000: final 249,773, max DD 15.3%, worst month -3.8%.
  - **v45.3 from $5,000 (tester, confirmed 2026-11-20): net +360,512, PF 1.63, max DD 16.4%, median month +4.8%, worst month -4.2%, losing months 12/47. Years $: 2023 -71, 2024 +2,775, 2025 +14,861, 2026 +343,118. Per 0.01 every year better than v45.2 (log section 40). Simulator: 374,143.**
  - v45.3 from $500 (tester): final 48,076, PF 1.64, but max DD 44.9% (June 2023, balance fell to ~$290), worst month -17.7%, 2023 +2 — min lot 0.01 = double the normal risk under $1,000. Advise >= $1,000 (ideally $5,000) or a cent account. A small-account London guard (v45.31, `InpLdnMaxMinLot`) was built and then CANCELLED by the user on 2026-11-21; the EA stays 45.30 (sim param `ldn_max_minlot_risk` kept, default off; log section 43).
  - Sim params = v45.2 dict + `use_s6=True, s6_bars=4, s6_vel=2.5`.
- Known weakness: calm years like 2023 are roughly flat (only the night engine made money in 2023). Nothing tried fixed 2023 without hurting other years.

## Demo accounts (both on MetaTrader VPS, local algo trading OFF; v45.2, user told to move both to v45.3 on 2026-11-20)
| Account | Broker / symbol | Balance | InpHourShift | VPS |
|---|---|---|---|---|
| 895781 | IFCMarkets-Demo, `XAUUSD` (spread ~46 pts) | ~$5,031 | -1 (server 1h behind Vantage) | Amsterdam |
| 26453869 | VantageMarkets-Demo, `XAUUSD+` (spread ~10 pts) | ~$959 | 0 | Ashburn |
- VPS auto-renew is OFF (about $15/month each). Hourly push "HiWin alive" from each.
- Next step agreed with the user: 2-4 weeks of demo, weekly account reports (History > right click > Report > HTML) compared trade by trade with the simulator. Then a real account of at least $5,000 on one broker (likely Vantage), no withdrawals for 3 months, then 30% of each winning month's profit, never touch capital, 6 months of living costs kept outside.

## Tools in this repo
- `data/xauusd_plus_m1_2023_2026.npz` — Vantage XAUUSD+ M1 bid + spread, 2023-01-03 .. 2026-11-20 (load with `sim.data.load_npz`).
- `sim/hiwin_sim.py` — event simulator of the EA, calibrated against the MT5 tester (about 99% of trades matched, yearly profit within ~5%). v45.2 parameters:
  `dict(use_b1=False, atr_hard_min_pct=0.14, recover_tp_atr=0.0, use_ldn=True, use_s4=True, use_trend=True, tr_risk_pct=0.25, ldn_sl_mult=1.75, sl_atr=7.0, tr_max_minlot_risk=1.0, use_night=True, night_sl_pct=0.5, night_min_prev_pct=1.0, night_lot_mult=1.0)`
- `python3 -m sim.account_run data/xauusd_plus_m1_2023_2026.npz "[('name', {params})]"` — full account ($5,000 default, `deposit=`), money by year and month.
- `python3 -m sim.research data/xauusd_plus_m1_2023_2026.npz "BASE_DICT" "[('name', {overrides}), ...]"` — fixed 0.01 lot, per-year net/DD for many variants in parallel.
- `python3 -m sim.calibrate_vs_report <npz> <report.html> "<params dict>"` — match the simulator against an MT5 report.
- `analysis/analyze_tester_report.py` — parse any MT5 tester report (HTML or PDF) into trades and rescue groups.
- `sim/engines.py` — stand-alone test engines (London, Donchian, session/prev-day breakouts, liquidity sweep, H1 momentum pullback).
- `sim/ml_filter.py` — walk-forward ML trade filter (tested, rejected).
- `analysis/v38_deep_analysis_AR.md` — full research log in Arabic (sections 1-40): every idea tried, with numbers.
- `docs/XAU_HiWin_v45.2_Summary_AR.pdf`, `docs/XAU_HiWin_v45.2_Guide_AR.pdf` — summary and operation guide for the user.

## Things already tried and rejected (do not re-propose without new evidence)
Tighter group stop, removing the recovery leg, break-even moves, second-chance reverse trades, monthly stop, drawdown throttle (too sensitive), NY breakout, previous-day breakout, fading London, ICT liquidity sweep, previous-day S/R rejection, S2/S3 setups, B1 breakout engine (lost 2024/2025), copying MyAiGold's visible rules (PF ~1.1), ALLYLLA's 3h break-even exit and rollover/weekend filters, ML trade filter, volatility-regime model, bigger night lot after a losing day, night lot > 2 (DD jumps), VWAP bands, Asian box + daily ATR filter / stop-order entry, M5 trend pullback + RSI reset, Z-score reversion, FVG, recovery only at support/resistance or multi-leg, time-of-day statistics matrix, efficiency-ratio friction->flow, A1 hybrid, entry-only S7/S8/S9/S10/S11/S12, S6 variants (volume climax, day extreme, M15, 4-6 bars, no-new-high) (log sections 28-39).

## Other bots the user looked at
- **MyAiGold** (MQL5 market, $900, AI, published 2026-09-04): per 0.01 lot +1,010 / +1,787 / +1,939 / +1,680 (2023-2026), monthly correlation with our bot 0.11 — a good companion if its live signals keep working; use Balance Step >= 1000. v44.1+ counts its own daily loss only, so it can share an account.
- **Gold Beaver** (MQL5 market product 177869, seller signal "القندس الذهبي" 27 weeks live, PF 7.66, copy $999/month — do not copy the signal): H4 swing high/low breakout stop orders refreshed every 4 h, two sets [A] (SL ~0.25-0.5%, TP ~0.4%) and [B] (SL ~0.9%, TP ~4%), instant break-even, stacks up to 6 orders. User tester Vantage 2023-2026, $5,000, Mode=15, Inp_Lot_Percent=11.6: +635,965, PF 6.8, positive every year (+1,298 / +4,081 / +42,788 / +586,832), worst month -6.4%, DD ~21% (2023). Top 50 trades = 93% of profit. Monthly correlation with v45.3 0.50; a 50/50 split cuts the monthly drawdown to 4.5% and makes 2023 +12% (log sections 45-46). Next: separate $5,000 Vantage demo, tester at lower risk and with IFC spread.
- **ALLYLLA Pullback Bot**: lost in 2023, correlation 0.83 with ours — not a useful companion.

## Automatic research
A scheduled job (trigger `trig_0126ag9zXpizb4C1oneAWY1z`, every 2 hours) was set up and then DISABLED at the user's request on 2026-11-20. If re-enabled, it follows `research/PROTOCOL.md`: one idea from `research/IDEAS.md` per run, results in `research/RESULTS_AR.md` (Arabic). Read those files to see what it found.

## Git
Work on branch `claude/bot-analysis-optimization-82i7f1`; commit and push there.
