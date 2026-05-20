import boto3
import pandas as pd
from moto.server import ThreadedMotoServer

BUCKET = "duckdb-demo-bucket"

df = pd.DataFrame({
    "event_id":   range(1, 11),
    "version":    ["0.9.0","0.10.0","1.0.0","1.0.0","1.1.0","1.1.0","1.2.0","1.2.0","1.2.0","1.2.0"],
    "client":     ["python-duckdb","duckdb-cli","python-duckdb","duckdb-r","duckdb-cli","python-duckdb","java-jdbc","node-duckdb","python-duckdb","duckdb-cli"],
    "query_type": ["SELECT","SELECT","INSERT","SELECT","COPY","SELECT","SELECT","INSERT","SELECT","SELECT"],
    "duration_ms":[120, 45, 300, 88, 512, 67, 200, 410, 55, 99],
})

server = ThreadedMotoServer(port=5000)
server.start()

s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id="mock",
    aws_secret_access_key="mock",
    endpoint_url="http://localhost:5000",
)

s3.create_bucket(Bucket=BUCKET)
s3.put_object(Bucket=BUCKET, Key="query_logs.csv", Body=df.to_csv(index=False))
print(f"Mock S3 running at http://localhost:5000")
print(f"Uploaded {len(df)} rows to s3://{BUCKET}/query_logs.csv")
print("Press Ctrl+C to stop.")

try:
    while True:
        pass
except KeyboardInterrupt:
    server.stop()
