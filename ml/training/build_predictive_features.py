import pandas as pd
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "Nfb5%kia"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "predictops"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

df = pd.read_sql("SELECT * FROM pipeline_logs", engine)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["dag_id", "timestamp"])

# Target: predict whether the NEXT run will fail
df["next_failed"] = (
    df.groupby("dag_id")["failed"]
    .transform(lambda x: x.shift(-1).rolling(window=3, min_periods=1).max())
)
df["next_sla_breach"] = df.groupby("dag_id")["sla_breach"].shift(-1)

# Use only past/current operational signals
df["prev_runtime"] = df.groupby("dag_id")["runtime_sec"].shift(1)
df["prev_rows"] = df.groupby("dag_id")["rows_processed"].shift(1)
df["prev_cpu"] = df.groupby("dag_id")["cpu_usage"].shift(1)
df["prev_memory"] = df.groupby("dag_id")["memory_usage"].shift(1)
df["prev_retries"] = df.groupby("dag_id")["retries"].shift(1)

df["runtime_avg_last_5"] = (
    df.groupby("dag_id")["runtime_sec"]
    .transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
)

df["rows_avg_last_5"] = (
    df.groupby("dag_id")["rows_processed"]
    .transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
)

df["retry_sum_last_5"] = (
    df.groupby("dag_id")["retries"]
    .transform(lambda x: x.shift(1).rolling(5, min_periods=1).sum())
)

df["failure_count_last_5"] = (
    df.groupby("dag_id")["failed"]
    .transform(lambda x: x.shift(1).rolling(5, min_periods=1).sum())
)

df["sla_breach_count_last_5"] = (
    df.groupby("dag_id")["sla_breach"]
    .transform(lambda x: x.shift(1).rolling(5, min_periods=1).sum())
)

df = df.dropna()

df.to_sql(
    "pipeline_predictive_features",
    engine,
    if_exists="replace",
    index=False
)

print("Predictive features created.")
print("Rows:", len(df))
print(df[["dag_id", "timestamp", "failed", "next_failed"]].head())
