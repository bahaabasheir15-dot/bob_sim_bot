"""Build the research-board data file from research/results.jsonl (used by the daily summary task)."""
import json, sys, datetime as dt
src = sys.argv[1] if len(sys.argv) > 1 else 'research/results.jsonl'
out = sys.argv[2] if len(sys.argv) > 2 else 'research/board.json'
rows = [json.loads(l) for l in open(src, encoding='utf-8') if l.strip()]
keys = ['date', 'track', 'idea', 'decision', 'y2023', 'y2024', 'y2025', 'y2026', 'total', 'dd', 'win_pct',
        'acc5k_final', 'acc5k_dd', 'acc2k_final', 'acc2k_dd', 'note']
rows = [{k: r.get(k) for k in keys} for r in rows]
meta = [{'label': 'Source', 'value': 'research/results.jsonl on branch claude/bot-analysis-optimization-82i7f1'},
        {'label': 'Built', 'value': dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')},
        {'label': 'Units', 'value': 'y2023..total, dd: simulator, fixed lot per 0.01 ($); acc*: full account runs'}]
json.dump({'rows': rows, 'meta': meta}, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print(len(rows), 'rows ->', out)
