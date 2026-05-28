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

df["runtime_rolling_avg"] = (
    df.groupby("dag_id")["runtime_sec"]
    .transform(lambda x: x.rolling(window=5, min_periods=1).mean())
)

df["rows_rolling_avg"] = (
    df.groupby("dag_id")["rows_processed"]
    .transform(lambda x: x.rolling(window=5, min_periods=1).mean())
)

df["retry_rolling_sum"] = (
    df.groupby("dag_id")["retries"]
    .transform(lambda x: x.rolling(window=5, min_periods=1).sum())
)

df["cpu_memory_pressure"] = df["cpu_usage"] * df["memory_usage"] / 100

df.to_sql(
    "pipeline_features",
    engine,
    if_exists="replace",
    index=False
)

print("Features created and saved to PostgreSQL.")
print(df.head())
