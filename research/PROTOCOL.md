# Automatic research protocol (read before every run)

You are one run of a scheduled research job. Each run tests ONE idea from `research/IDEAS.md`, records the
result, and stops. The user does not read English: anything written FOR THE USER (the summary at the end of
`research/RESULTS_AR.md`) must be in Egyptian Arabic.

## Setup (every run)
1. Work in the repository `bahaabasheir15-dot/bob_sim_bot`, branch `claude/bot-analysis-optimization-82i7f1`
   (fetch it and merge it into whatever branch you are given, so you start from the latest results).
2. Read `CLAUDE.md`, this file, `research/IDEAS.md`, and the last entries of `research/RESULTS_AR.md`.
3. `pip install -q scikit-learn` only if the idea needs it. Data: `data/xauusd_plus_m1_2023_2026.npz`
   (load with `sim.data.load_npz`). Baseline v45.2 parameters are in `CLAUDE.md`.

## Pick the idea
- Take the FIRST idea in `research/IDEAS.md` whose status is `TODO`. Change it to `IN PROGRESS (run <UTC time>)`
  and commit + push that line immediately, so a run that starts while you work picks a different idea.
- If an idea has been `IN PROGRESS` for more than 3 hours, treat it as `TODO`.
- If there is no `TODO` idea left, write 3-5 NEW ideas (never one already in the rejected list in `CLAUDE.md`,
  `analysis/v38_deep_analysis_AR.md` or `research/RESULTS_AR.md`), add them as `TODO`, then test the first.

## Test it (honestly)
1. Implement the idea in the simulator (`sim/hiwin_sim.py`) as a NEW parameter whose default reproduces v45.2
   exactly. Check that the baseline still gives: `$5,000 account final 249,773, max DD 15.3%`.
2. Fixed-lot test: `python3 -m sim.research data/xauusd_plus_m1_2023_2026.npz "<v45.2 dict>" "[variants]"`
   with the idea at 3+ nearby settings.
3. Account test: `python3 -m sim.account_run ...` on $5,000 and on $1,000 for the best and the middle setting.
4. ACCEPT only if ALL are true:
   - fixed lot: net is higher in EACH of 2023, 2024, 2025, 2026 (or equal within 2% and DD lower that year);
   - at least 2 of the 3 nearby settings also pass;
   - account run: max DD not higher, worst month not worse by more than 0.5 point;
   - it makes sense as market behaviour, not just a number that happened to fit.
   Otherwise REJECT. Most ideas should be rejected; that is normal and honest.

## Record
- `research/IDEAS.md`: set the status to `ACCEPTED` or `REJECTED` with a one-line reason.
- `research/RESULTS_AR.md`: append a section in Egyptian Arabic: the idea in simple words, the table of numbers
  per year, the decision and why. Keep it short.
- If ACCEPTED: create the next EA version file in `ea/` (copy the latest, implement the change exactly as in the
  simulator, new version number, SAME magic number 20263255, header comment with the evidence), update the
  "Current state" section of `CLAUDE.md` to say a NEW CANDIDATE exists and is NOT yet tested in MT5 or deployed.
  Never tell the user to deploy it before an MT5 tester run confirms it.
- Commit and push. If the push is rejected, fetch, merge, and push again.

## Hard rules
- Never change the live settings of the user's accounts and never claim something was deployed.
- Never accept an idea that only works in some years. Never tune on one year.
- Never raise risk (lot size, risk %) as an "improvement"; risk level is the user's decision.
- One idea per run. Stop after recording it.
