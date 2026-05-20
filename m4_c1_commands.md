# DuckDB m4_c1 Reading Files Directly — CSV, Parquet, Excel, JSON

To start a duckdb ephmeral session:

```
duckdb
```

---

## duckdb_releases.csv

```sql
-- Preview all rows
SELECT * FROM read_csv_auto('m4/data/duckdb_releases.csv');

-- Star growth between releases
SELECT
    version,
    release_date,
    github_stars_approx,
    github_stars_approx - LAG(github_stars_approx) OVER (ORDER BY release_date) AS stars_gained
FROM read_csv_auto('m4/data/duckdb_releases.csv')
ORDER BY release_date;
```

---

## duckdb_extensions.json

```sql
-- Select all raw JSON
SELECT * FROM read_json_auto('m4/data/duckdb_extensions.json');

-- Extensions by category
SELECT ext.category, LIST(ext.name ORDER BY ext.name) AS extensions
FROM (
    SELECT UNNEST(duckdb_extensions) AS ext
    FROM read_json_auto('m4/data/duckdb_extensions.json')
)
GROUP BY ext.category
ORDER BY ext.category;
```

---

## duckdb_community_events.parquet

```sql
-- Preview all events
SELECT * FROM read_parquet('m4/data/duckdb_community_events.parquet');

-- Event name and URL
SELECT event_name, url FROM read_parquet('m4/data/duckdb_community_events.parquet');
```

---

## duckdb_community.xlsx

```sql
-- Requires the excel extension
INSTALL excel;
LOAD excel;

-- Preview community metrics sheet
SELECT * FROM read_xlsx('m4/data/duckdb_community.xlsx', sheet='Community Metrics');

-- Metrics with the highest growth
SELECT metric, yoy_growth_pct, value_2024, value_2025
FROM read_xlsx('m4/data/duckdb_community.xlsx', sheet='Community Metrics')
ORDER BY yoy_growth_pct DESC
LIMIT 5;
```

---

## clickstream_events.csv  →  cache to Parquet

```sql
-- Cache CSV to Parquet (run once)
COPY (SELECT * FROM read_csv_auto('m4/data/clickstream_events.csv'))
TO 'm4/data/clickstream_events.parquet'
(FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000);

-- Revenue by region from Parquet cache
SELECT
    region,
    SUM(revenue_usd) AS total_revenue,
    COUNT(*)         AS events
FROM read_parquet('m4/data/clickstream_events.parquet')
GROUP BY region
ORDER BY total_revenue DESC;

-- Benchmark: compare CSV vs Parquet query time
.timer on
SELECT region, SUM(revenue_usd) AS total_revenue
FROM read_csv_auto('m4/data/clickstream_events.csv')
GROUP BY region ORDER BY total_revenue DESC;

SELECT region, SUM(revenue_usd) AS total_revenue
FROM read_parquet('m4/data/clickstream_events.parquet')
GROUP BY region ORDER BY total_revenue DESC;
.timer off
```

---

## Querying files hosted on GitHub

Replace `{user}` and `{repo}` with your GitHub username and repository name.

```sql
-- Load the httpfs extension to enable remote file reads
INSTALL httpfs;
LOAD httpfs;

-- CSV from GitHub raw
SELECT * FROM read_csv_auto('https://raw.githubusercontent.com/{user}/{repo}/main/m4/data/duckdb_releases.csv');

-- Parquet from GitHub raw
SELECT * FROM read_parquet('https://raw.githubusercontent.com/{user}/{repo}/main/m4/data/duckdb_community_events.parquet');

-- JSON from GitHub raw
SELECT ext.name, ext.category, ext.description
FROM (
    SELECT UNNEST(duckdb_extensions) AS ext
    FROM read_json_auto('https://raw.githubusercontent.com/{user}/{repo}/main/m4/data/duckdb_extensions.json')
);

-- Benchmark Parquet over HTTP vs local
.timer on
SELECT region, SUM(revenue_usd) AS total_revenue
FROM read_parquet('https://raw.githubusercontent.com/{user}/{repo}/main/m4/data/clickstream_events.parquet')
GROUP BY region ORDER BY total_revenue DESC;
.timer off
```
