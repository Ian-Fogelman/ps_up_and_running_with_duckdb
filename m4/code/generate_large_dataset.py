"""
generate_large_dataset.py

Uses DuckDB's built-in data generation functions to produce a large
web-analytics clickstream CSV (~300 000 rows, ~35 MB) that is safe to
commit to GitHub.  The file is written to m4/data/.

Run this once; the output is consumed by cache_to_parquet.py.
"""

import duckdb
import time
from pathlib import Path

OUT_DIR  = Path(__file__).parent.parent / "data"
OUT_FILE = OUT_DIR / "clickstream_events.csv"
ROWS     = 300_000

con = duckdb.connect()

print(f"Generating {ROWS:,} rows with DuckDB …")
t0 = time.perf_counter()

con.execute(f"""
COPY (
    WITH base AS (
        SELECT
            -- surrogate key
            row_number() OVER ()                                    AS event_id,

            -- timestamp spread over ~2 years
            TIMESTAMP '2023-01-01 00:00:00'
                + INTERVAL (CAST(random() * 63072000 AS INT)) SECOND AS event_ts,

            -- synthetic user / session IDs
            CAST(1 + CAST(random() * 49999 AS INT) AS INT)          AS user_id,
            printf('sess_%08x',
                CAST(random() * 4294967295 AS BIGINT))              AS session_id,

            -- categorical fields
            CASE CAST(random() * 7 AS INT)
                WHEN 0 THEN 'page_view'
                WHEN 1 THEN 'click'
                WHEN 2 THEN 'scroll'
                WHEN 3 THEN 'form_submit'
                WHEN 4 THEN 'video_play'
                WHEN 5 THEN 'download'
                ELSE         'search'
            END                                                     AS event_type,

            CASE CAST(random() * 8 AS INT)
                WHEN 0 THEN '/home'
                WHEN 1 THEN '/docs/quickstart'
                WHEN 2 THEN '/docs/api'
                WHEN 3 THEN '/blog'
                WHEN 4 THEN '/pricing'
                WHEN 5 THEN '/download'
                WHEN 6 THEN '/community'
                ELSE         '/changelog'
            END                                                     AS page_path,

            CASE CAST(random() * 6 AS INT)
                WHEN 0 THEN 'us-east'
                WHEN 1 THEN 'us-west'
                WHEN 2 THEN 'eu-west'
                WHEN 3 THEN 'eu-central'
                WHEN 4 THEN 'ap-south'
                ELSE         'ap-east'
            END                                                     AS region,

            CASE CAST(random() * 4 AS INT)
                WHEN 0 THEN 'chrome'
                WHEN 1 THEN 'firefox'
                WHEN 2 THEN 'safari'
                ELSE         'edge'
            END                                                     AS browser,

            -- numeric fields
            50 + CAST(random() * 29950 AS INT)                     AS duration_ms,
            ROUND(CASE WHEN random() < 0.05
                       THEN ROUND(random() * 499 + 1, 2)
                       ELSE 0.0 END, 2)                             AS revenue_usd,

            -- derived boolean
            NULL                                                    AS _placeholder

        FROM range({ROWS})
    )
    SELECT
        event_id,
        event_ts,
        user_id,
        session_id,
        event_type,
        page_path,
        region,
        browser,
        duration_ms,
        revenue_usd,
        revenue_usd > 0                                             AS is_conversion
    FROM base
    ORDER BY event_ts          -- realistic time-ordered log
)
TO '{OUT_FILE.as_posix()}'
(FORMAT CSV, HEADER TRUE)
""")

elapsed = time.perf_counter() - t0
size_mb = OUT_FILE.stat().st_size / 1_048_576
print(f"Done in {elapsed:.1f}s  |  {size_mb:.1f} MB  ->  {OUT_FILE}")
