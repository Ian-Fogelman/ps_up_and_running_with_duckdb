# Demo 3: Saving and Reusing Query Output

Exporting results to CSV and Parquet with `COPY TO`, and wrapping reusable logic into macros for efficient, repeatable analysis.

---

## Start a persistent DuckDB session

```bash
duckdb demo.duckdb
```

---

## Load the source data

```sql
CREATE TABLE releases AS
SELECT * FROM read_csv_auto('m4/data/duckdb_releases.csv');

CREATE TABLE events AS
SELECT * FROM read_parquet('m4/data/duckdb_community_events.parquet');
```

---

## COPY TO - Export results to CSV

```sql
COPY (
    SELECT * FROM releases WHERE YEAR(release_date) >= 2024
) TO 'm4/data/releases_2024_plus.csv' (FORMAT CSV, HEADER TRUE);
```

---

## COPY TO - Export results to Parquet

```sql
COPY (
    SELECT * FROM events WHERE event_type = 'Conference'
) TO 'm4/data/conferences.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

---

## Macros - Scalar macro

```sql
CREATE MACRO stars_gained(current, previous) AS (current - previous);

SELECT version, github_stars_approx,
    stars_gained(github_stars_approx, LAG(github_stars_approx) OVER (ORDER BY release_date)) AS gained
FROM releases;
```

---

## Macros - Table macro

```sql
CREATE MACRO events_by_city(city_name) AS TABLE
    SELECT event_name, event_date, event_type, attendees_est
    FROM events
    WHERE city = city_name
    ORDER BY event_date;

SELECT * FROM events_by_city('Amsterdam');
SELECT * FROM events_by_city('Seattle');
```

---

## Verify exports

```sql
SELECT * FROM read_csv_auto('m4/data/releases_2024_plus.csv');
SELECT * FROM read_parquet('m4/data/conferences.parquet');
```
