import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("Connecting to:", DB_HOST, DB_PORT, DB_NAME)

engine = create_engine(DATABASE_URL)

df = pd.read_sql("SELECT * FROM pipeline_logs", engine)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["dag_id", "timestamp"]).reset_index(drop=True)

group = df.groupby("dag_id")

def future_max(series, window=3):
    return series.shift(-1).rolling(window=window, min_periods=1).max().shift(-(window - 1))

# Target 1: exact next run failure
df["next_failed_1run"] = group["failed"].shift(-1)

df["next_failed"] = group["failed"].transform(
    lambda x: future_max(x, window=3)
)

df["next_sla_breach"] = group["sla_breach"].shift(-1)


# Previous run features
df["prev_runtime"] = group["runtime_sec"].shift(1)
df["prev_rows"] = group["rows_processed"].shift(1)
df["prev_cpu"] = group["cpu_usage"].shift(1)
df["prev_memory"] = group["memory_usage"].shift(1)
df["prev_retries"] = group["retries"].shift(1)

# Rolling averages
df["runtime_avg_last_5"] = group["runtime_sec"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=1).mean()
)

df["rows_avg_last_5"] = group["rows_processed"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=1).mean()
)

df["cpu_avg_last_5"] = group["cpu_usage"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=1).mean()
)

df["memory_avg_last_5"] = group["memory_usage"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=1).mean()
)

# Rolling volatility
df["runtime_std_last_5"] = group["runtime_sec"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=2).std()
)

df["rows_std_last_5"] = group["rows_processed"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=2).std()
)

df["cpu_std_last_5"] = group["cpu_usage"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=2).std()
)

df["memory_std_last_5"] = group["memory_usage"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=2).std()
)

df["runtime_avg_last_10"] = group["runtime_sec"].transform(
    lambda x: x.shift(1).rolling(10, min_periods=2).mean()
)

df["rows_avg_last_10"] = group["rows_processed"].transform(
    lambda x: x.shift(1).rolling(10, min_periods=2).mean()
)

df["cpu_avg_last_10"] = group["cpu_usage"].transform(
    lambda x: x.shift(1).rolling(10, min_periods=2).mean()
)

df["memory_avg_last_10"] = group["memory_usage"].transform(
    lambda x: x.shift(1).rolling(10, min_periods=2).mean()
)

df["runtime_std_last_10"] = group["runtime_sec"].transform(
    lambda x: x.shift(1).rolling(10, min_periods=2).std()
)

df["cpu_std_last_10"] = group["cpu_usage"].transform(
    lambda x: x.shift(1).rolling(10, min_periods=2).std()
)

df["memory_std_last_10"] = group["memory_usage"].transform(
    lambda x: x.shift(1).rolling(10, min_periods=2).std()
)

# Rolling counts
df["retry_sum_last_5"] = group["retries"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=1).sum()
)

df["failure_count_last_5"] = group["failed"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=1).sum()
)

df["sla_breach_count_last_5"] = group["sla_breach"].transform(
    lambda x: x.shift(1).rolling(5, min_periods=1).sum()
)

# Trend / change features
df["runtime_change"] = df["prev_runtime"] - group["runtime_sec"].shift(2)
df["rows_change"] = df["prev_rows"] - group["rows_processed"].shift(2)
df["cpu_change"] = df["prev_cpu"] - group["cpu_usage"].shift(2)
df["memory_change"] = df["prev_memory"] - group["memory_usage"].shift(2)
df["retries_change"] = df["prev_retries"] - group["retries"].shift(2)

df["runtime_vs_avg"] = df["prev_runtime"] - df["runtime_avg_last_5"]
df["rows_vs_avg"] = df["prev_rows"] - df["rows_avg_last_5"]
df["cpu_vs_avg"] = df["prev_cpu"] - df["cpu_avg_last_5"]
df["memory_vs_avg"] = df["prev_memory"] - df["memory_avg_last_5"]

df["runtime_ratio"] = df["prev_runtime"] / (df["runtime_avg_last_5"] + 1)
df["rows_ratio"] = df["prev_rows"] / (df["rows_avg_last_5"] + 1)
df["cpu_ratio"] = df["prev_cpu"] / (df["cpu_avg_last_5"] + 1)
df["memory_ratio"] = df["prev_memory"] / (df["memory_avg_last_5"] + 1)

# Z-score style anomaly features
df["runtime_zscore"] = df["runtime_vs_avg"] / (df["runtime_std_last_5"] + 1)
df["rows_zscore"] = df["rows_vs_avg"] / (df["rows_std_last_5"] + 1)
df["cpu_zscore"] = df["cpu_vs_avg"] / (df["cpu_std_last_5"] + 1)
df["memory_zscore"] = df["memory_vs_avg"] / (df["memory_std_last_5"] + 1)

# Pressure / instability features
df["resource_pressure"] = df["prev_cpu"] * df["prev_memory"]
df["runtime_resource_pressure"] = df["prev_runtime"] * df["prev_cpu"] * df["prev_memory"]
df["retry_failure_pressure"] = df["retry_sum_last_5"] + (df["failure_count_last_5"] * 3)
df["sla_failure_pressure"] = df["sla_breach_count_last_5"] + (df["failure_count_last_5"] * 3)

df["instability_score"] = (
    df["retry_sum_last_5"]
    + df["failure_count_last_5"] * 3
    + df["sla_breach_count_last_5"] * 2
    + df["runtime_zscore"].abs()
    + df["cpu_zscore"].abs()
    + df["memory_zscore"].abs()
)

# Clean bad values
df = df[df["next_failed"].notna()]
df = df[df["next_failed_1run"].notna()]

df = df.replace([float("inf"), -float("inf")], 0)
df = df.fillna(0)

df["next_failed"] = df["next_failed"].astype(int)
df["next_failed_1run"] = df["next_failed_1run"].astype(int)

df.to_sql(
    "pipeline_predictive_features",
    engine,
    if_exists="replace",
    index=False
)

print("Predictive features created.")
print("Rows:", len(df))
print("Target distribution:")
print(df["next_failed"].value_counts(normalize=True))
print(df[["dag_id", "timestamp", "failed", "next_failed"]].head())
