# DuckDB m4_c1 CLI Query Commands

To start a duckdb ephmeral session:

```
duckdb
```

---

```
CREATE TABLE duckdb_releases AS SELECT * FROM 'm4/data/duckdb_releases.csv'; 
```

```sql
CREATE VIEW duckdb_releases_2022 AS
SELECT * FROM 'm4/data/duckdb_releases.csv'
WHERE YEAR(release_date) = 2022;
```

```sql
-- Show all available views
SHOW ALL TABLES;

-- Or query the information schema directly
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_type = 'VIEW';
```

---

## Mock S3 Bucket

Install dependencies first:

```bash
pip install -r requirements.txt
```

Start the mock S3 server and populate the bucket:

```bash
python m4/code/mock_s3.py
```

Query the uploaded data with DuckDB:

```sql
-- Load httpfs to enable S3 reads
INSTALL httpfs;
LOAD httpfs;

-- Configure mock S3 credentials
CREATE SECRET mock_s3 (
    TYPE s3,
    KEY_ID 'mock',
    SECRET 'mock',
    REGION 'us-east-1',
    ENDPOINT 'localhost:5000',
    USE_SSL false,
    URL_STYLE 'path'
);

-- Query the uploaded CSV directly from the mock bucket
SELECT * FROM read_csv_auto('s3://duckdb-demo-bucket/query_logs.csv');

-- Aggregate by client
SELECT client, COUNT(*) AS queries, AVG(duration_ms) AS avg_ms
FROM read_csv_auto('s3://duckdb-demo-bucket/query_logs.csv')
GROUP BY client
ORDER BY avg_ms DESC;
```