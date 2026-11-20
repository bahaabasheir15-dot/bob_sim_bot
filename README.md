# XAU HiWin EA

| Path | What |
|---|---|
| `ea/XAU_HiWin_EA_DUAL_LEAN_v38.mq5` | v38 baseline (magic 20263248) |
| `ea/XAU_HiWin_EA_DUAL_LEAN_v39.mq5` | v39: ATR floor 5.5, optional group stop, per-trade CSV log (magic 20263249) |
| `ea/XAU_HiWin_EA_DUAL_LEAN_v40.mq5` | v40: v39 with ATR floors in % of price, so it trades at any gold price (magic 20263250) |
| `ea/XAU_HiWin_EA_DUAL_LEAN_v41.mq5` | v41: scalper only (B1 off), ATR floor 0.14% of price (magic 20263251) |
| `ea/XAU_HiWin_EA_v42.mq5` | v42: scalper + London breakout engine (L1), recovery group target 0 (magic 20263252) |
| `ea/XAU_HiWin_EA_v43.mq5` | v43: v42 + scalper setup S4 + H1 trend engine (T1) at 0.25% risk (magic 20263253) |
| `sim/` | Python simulator of the EA on M1 data (Dukascopy or an MT5 bar export) |
| `analysis/v38_deep_analysis_AR.md` | Deep analysis of the v38 tester report and the v39 test plan (Arabic) |
| `analysis/analyze_tester_report.py` | Rebuilds trades and recovery groups from any MT5 tester-report PDF: `python3 analysis/analyze_tester_report.py report.pdf` (needs `pdftotext`) |
