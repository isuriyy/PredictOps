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

df = pd.read_csv("data/synthetic/pipeline_logs.csv")

df.to_sql(
    "pipeline_logs",
    engine,
    if_exists="replace",
    index=False
)

print("Pipeline logs loaded into PostgreSQL.")
print("Rows loaded:", len(df))
