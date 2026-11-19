#!/usr/bin/env python3
"""Download Dukascopy XAUUSD M1 candles (bid + ask) as raw .bi5 files.

    python3 download_dukascopy.py OUT_DIR 2023-01-01 2026-11-19
Files: OUT_DIR/YYYY/MM/DD_{BID,ASK}.bi5  (MM is 1-based here). Re-running skips files already present.
"""
import datetime as dt, os, sys, time, urllib.request

def main(out, start, end):
    d = dt.date.fromisoformat(start); e = dt.date.fromisoformat(end)
    while d <= e:
        if d.weekday() != 5:  # Saturday has no gold trading
            for side in ('BID', 'ASK'):
                p = os.path.join(out, f'{d.year}', f'{d.month:02d}', f'{d.day:02d}_{side}.bi5')
                if os.path.exists(p):
                    continue
                os.makedirs(os.path.dirname(p), exist_ok=True)
                url = (f'https://datafeed.dukascopy.com/datafeed/XAUUSD/{d.year}/{d.month - 1:02d}/'
                       f'{d.day:02d}/{side}_candles_min_1.bi5')
                for attempt in range(30):
                    try:
                        with urllib.request.urlopen(url, timeout=30) as r:
                            data = r.read()
                        open(p, 'wb').write(data)
                        break
                    except urllib.error.HTTPError as ex:
                        if ex.code == 404:
                            open(p, 'wb').write(b''); break
                        time.sleep(60 if ex.code == 429 else 5)   # the server rate-limits hard
                    except Exception:
                        time.sleep(2 * (attempt + 1))
                time.sleep(1.0)
        d += dt.timedelta(days=1)

if __name__ == '__main__':
    main(*sys.argv[1:4])
