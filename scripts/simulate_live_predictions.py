import pandas as pd
import requests
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

query = """
SELECT *
FROM pipeline_predictive_features
ORDER BY timestamp DESC
LIMIT 20
"""

df = pd.read_sql(query, engine)

API_URL = "http://127.0.0.1:8000/predict-risk"

for _, row in df.iterrows():

    payload = {
        "prev_runtime": row["prev_runtime"],
        "prev_rows": row["prev_rows"],
        "prev_cpu": row["prev_cpu"],
        "prev_memory": row["prev_memory"],
        "prev_retries": int(row["prev_retries"]),
        "runtime_avg_last_5": row["runtime_avg_last_5"],
        "rows_avg_last_5": row["rows_avg_last_5"],
        "retry_sum_last_5": int(row["retry_sum_last_5"]),
        "failure_count_last_5": int(row["failure_count_last_5"]),
        "sla_breach_count_last_5": int(row["sla_breach_count_last_5"])
    }

    response = requests.post(API_URL, json=payload)

    print(response.json())
