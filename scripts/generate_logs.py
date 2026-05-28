import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

NUM_RECORDS_PER_PIPELINE = 10000

pipelines = [
    "sales_etl",
    "customer_sync",
    "payment_pipeline",
    "inventory_refresh",
    "recommendation_engine"
]

data = []
start_date = datetime.now() - timedelta(days=90)

for dag_id in pipelines:
    health = 1.0
    timestamp = start_date

    for run_id in range(NUM_RECORDS_PER_PIPELINE):
        timestamp += timedelta(minutes=random.randint(5, 30))

        # Random degradation and recovery
        if random.random() < 0.08:
            health -= random.uniform(0.05, 0.15)

        if random.random() < 0.05:
            health += random.uniform(0.03, 0.10)

        health = max(0.0, min(1.0, health))

        stress = 1.0 - health

        runtime_sec = np.random.normal(280 + stress * 300, 40)
        rows_processed = int(np.random.normal(100000 - stress * 50000, 15000))
        cpu_usage = np.random.normal(50 + stress * 45, 8)
        memory_usage = np.random.normal(55 + stress * 40, 8)
        retries = np.random.poisson(stress * 4)

        failure_probability = 0.01 + (stress ** 3) * 0.85
        failed = 1 if random.random() < failure_probability else 0

        sla_breach = 1 if runtime_sec > 450 else 0

        # Recovery after failure
        if failed == 1:
            health += random.uniform(0.10, 0.25)
            health = min(1.0, health)

        data.append({
            "timestamp": timestamp,
            "dag_id": dag_id,
            "runtime_sec": round(max(runtime_sec, 30), 2),
            "rows_processed": max(rows_processed, 1000),
            "cpu_usage": round(min(max(cpu_usage, 5), 100), 2),
            "memory_usage": round(min(max(memory_usage, 5), 100), 2),
            "retries": retries,
            "failed": failed,
            "sla_breach": sla_breach
        })

df = pd.DataFrame(data)

df.to_csv("data/synthetic/pipeline_logs.csv", index=False)

print("New realistic synthetic pipeline logs generated.")
print("Rows:", len(df))
print(df["failed"].value_counts())
print(df.head())
