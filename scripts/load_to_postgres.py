import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
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

df = pd.read_csv("data/synthetic/pipeline_logs.csv")

df.to_sql(
    "pipeline_logs",
    engine,
    if_exists="replace",
    index=False
)

with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM pipeline_logs")).scalar()

print("Pipeline logs loaded into PostgreSQL.")
print("Rows loaded:", count)
