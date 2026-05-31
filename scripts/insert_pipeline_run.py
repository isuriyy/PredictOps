import sys
import random
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from config import DB_USER, DB_PASSWORD, DB_NAME

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@localhost:5433/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

def generate_pipeline_run():
    is_risky = random.choice([True, False, False])

    if is_risky:
        return {
            "pipeline_name": "sales_etl",
            "run_time": datetime.now(),
            "runtime_seconds": round(random.uniform(400, 650), 2),
            "rows_processed": random.randint(30000, 50000),
            "cpu_usage": round(random.uniform(75, 95), 2),
            "memory_usage": round(random.uniform(80, 96), 2),
            "retries": random.randint(2, 5),
            "status": "WARNING",
            "failure_risk_score": round(random.uniform(0.7, 0.98), 3),
            "risk_level": "HIGH",
        }

    return {
        "pipeline_name": "sales_etl",
        "run_time": datetime.now(),
        "runtime_seconds": round(random.uniform(100, 250), 2),
        "rows_processed": random.randint(60000, 90000),
        "cpu_usage": round(random.uniform(20, 55), 2),
        "memory_usage": round(random.uniform(30, 65), 2),
        "retries": random.randint(0, 1),
        "status": "SUCCESS",
        "failure_risk_score": round(random.uniform(0.1, 0.39), 3),
        "risk_level": "LOW",
    }


run = generate_pipeline_run()

pd.DataFrame([run]).to_sql(
    "pipeline_runs",
    engine,
    if_exists="append",
    index=False,
)

print("Pipeline run inserted:")
print(run)
