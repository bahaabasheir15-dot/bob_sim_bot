# XAU HiWin EA

| Path | What |
|---|---|
| `ea/XAU_HiWin_EA_DUAL_LEAN_v38.mq5` | v38 baseline (magic 20263248) |
| `ea/XAU_HiWin_EA_DUAL_LEAN_v39.mq5` | v39: ATR floor 5.5, optional group stop, per-trade CSV log (magic 20263249) |
| `ea/XAU_HiWin_EA_DUAL_LEAN_v40.mq5` | v40: v39 with ATR floors in % of price, so it trades at any gold price (magic 20263250) |
| `sim/` | Python simulator of the EA on M1 data (Dukascopy or an MT5 bar export) |
| `analysis/v38_deep_analysis_AR.md` | Deep analysis of the v38 tester report and the v39 test plan (Arabic) |
| `analysis/analyze_tester_report.py` | Rebuilds trades and recovery groups from any MT5 tester-report PDF: `python3 analysis/analyze_tester_report.py report.pdf` (needs `pdftotext`) |
