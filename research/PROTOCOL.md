# Research team protocol (read before every run)

Three scheduled research tracks run every night, each in a fresh cloud session. Each run tests ONE idea from
its own queue, records the result honestly, and stops. The user reads only Egyptian Arabic: everything written
FOR THE USER must be in Egyptian Arabic (file names / settings / code stay in English in backticks).

| Track | Queue file | Goal |
|---|---|---|
| A | `research/TRACK_A_loss_to_profit.md` | turn losing trades / baskets / days into profit (rescue, exits, re-entries) |
| B | `research/TRACK_B_keep_profit.md`    | keep what was won: lower max DD and worst month, fix calm years (2023) |
| C | `research/TRACK_C_winrate.md`        | raise the win rate (trade level AND basket level) WITHOUT lowering net profit |

## Setup (every run)
1. Repository `bahaabasheir15-dot/bob_sim_bot`. `git fetch origin claude/bot-analysis-optimization-82i7f1` and merge
   it into your branch first, so you start from the latest results of all tracks.
2. Read `CLAUDE.md`, this file, your track's queue file, the end of `research/RESULTS_AR.md`, and the rejected
   list in `CLAUDE.md` + `analysis/v38_deep_analysis_AR.md` (sections 28-77). NEVER re-test a rejected idea
   without a clearly new mechanism.
3. Data: `data/xauusd_plus_m1_2023_2026.npz` (load with `sim.data.load_npz`). Simulator: `sim/hiwin_sim.py`.

## Baseline = v45.7 (the best version; every idea is compared to it)
```
V457 = dict(use_b1=False, atr_hard_min_pct=0.14, recover_tp_atr=0.0, use_ldn=True, use_s4=True, use_trend=False,
 tr_risk_pct=0.25, ldn_sl_mult=1.75, sl_atr=7.0, tr_max_minlot_risk=1.0, use_night=True, night_sl_pct=0.5,
 night_min_prev_pct=1.0, s6_bars=4, s6_vel=2.5, use_s6=True, use_swing=True, sw_risk_pct=0.5, night_hold_h=12,
 sw_be_pct=0.3, night_lot_mult=1.5)
```
- Fixed lot 0.01 (normalise every trade to 0.01: `net / lots * 0.01`): 2023 +323 / 2024 +1,120 / 2025 +3,750 /
  2026 +6,871 = 12,063, max DD 395. Trade win rate 74.6%; scalp-basket win rate 80.9%.
  `sim.research` does this: `python3 -m sim.research data/xauusd_plus_m1_2023_2026.npz "V457" "[variants]"`.
- Account `python3 -m sim.account_run data/xauusd_plus_m1_2023_2026.npz "[('name', dict(V457, deposit=5000.0))]"`:
  $5,000 -> final 1,475,653, max DD 16.6%, worst month -7.3%, years +761 / +5,364 / +55,573 / +1,408,955.
  $2,000 -> final 813,154, max DD 18.9%, worst month -9.9%, years +393 / +1,765 / +19,514 / +789,482.
- Note: lot-size multipliers cannot be tested at fixed 0.01 (rounding) -> use account runs for sizing ideas.
- Runs take minutes: run variants in background processes (one `account_run` variant per process, max 4).

## Pick the idea
- Take the FIRST `TODO` idea in your track file, set it to `IN PROGRESS (<UTC time>)`, commit + push at once.
- `IN PROGRESS` older than 6 hours counts as `TODO`.
- If no `TODO` is left: write 3-5 NEW ideas for your track's goal (not rejected before), add them, test the first.

## Test it (honestly)
1. Add the idea to `sim/hiwin_sim.py` as a NEW parameter, default OFF, and check the baseline numbers above
   are reproduced exactly with it off.
2. Fixed-lot test of the idea at 3+ nearby settings (or account runs for sizing ideas).
3. Account runs at $5,000 AND $2,000 for the middle setting.
4. ACCEPT only if ALL are true:
   - net higher in EACH year 2023, 2024, 2025, 2026 (or equal within 2% with lower DD that year);
   - at least 2 of 3 nearby settings also pass (no isolated lucky value);
   - account runs: max DD not higher by more than 0.5 point, worst month not worse by more than 0.5 point;
   - Track C only: the win rate rises AND total net is not lower;
   - it makes sense as market behaviour.
   Otherwise REJECT. Most ideas are rejected; that is normal and honest.

## Record (every run, accepted or not)
- Track file: status `ACCEPTED` / `REJECTED (<one-line reason>)`.
- `research/RESULTS_AR.md`: append `## [<track letter>] <date> — <idea>` in Egyptian Arabic: the idea in simple words,
  numbers per year (fixed lot) + account runs, the decision and why. Short.
- `research/results.jsonl`: append ONE json line:
  `{"date":"YYYY-MM-DD","track":"A","idea":"<short Arabic title>","decision":"ACCEPTED|REJECTED",
    "y2023":..,"y2024":..,"y2025":..,"y2026":..,"total":..,"dd":..,"win_pct":..,
    "acc5k_final":..,"acc5k_dd":..,"acc2k_final":..,"acc2k_dd":..,"note":"<one Arabic line>"}`
  (fixed-lot numbers per 0.01; use null for anything not measured).
- If ACCEPTED: create the next EA candidate in `ea/` (copy `ea/XAU_HiWin_EA_v45_7.mq5`, or the newest accepted
  candidate, implement the change exactly as in the simulator, new version number, SAME magic 20263255, header
  comment with the evidence). Add one line to `CLAUDE.md` "Current state": NEW CANDIDATE, NOT tested in MT5,
  NOT deployed.
- Commit, then push to `claude/bot-analysis-optimization-82i7f1` (fetch + merge and push again if rejected; if
  pushing there is not allowed, push your own branch and say so in the result line).
- `git checkout -- sim/__pycache__` before committing.

## Hard rules
- Never touch the user's live accounts, never say something was deployed, never tell the user to deploy a
  candidate before an MT5 tester run confirms it.
- Never accept an idea that works only in some years; never tune on one year.
- Never raise risk (lot, risk %) and call it an improvement; a bigger lot is the user's decision.
- One idea per run. Stop after recording it.
