import random
from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator


PREDICT_RISK_API_URL = "http://api:8000/predict-risk"
PIPELINE_RUN_API_URL = "http://api:8000/pipeline-run"


def generate_pipeline_metrics():
    is_risky = random.choice([True, False, False])

    if is_risky:
        return {
            "prev_runtime": round(random.uniform(400, 650), 2),
            "prev_rows": random.randint(30000, 50000),
            "prev_cpu": round(random.uniform(75, 95), 2),
            "prev_memory": round(random.uniform(80, 96), 2),
            "prev_retries": random.randint(2, 5),
            "runtime_avg_last_5": round(random.uniform(350, 550), 2),
            "rows_avg_last_5": random.randint(35000, 60000),
            "retry_sum_last_5": random.randint(5, 12),
            "failure_count_last_5": random.randint(1, 4),
            "sla_breach_count_last_5": random.randint(1, 4),
        }

    return {
        "prev_runtime": round(random.uniform(100, 250), 2),
        "prev_rows": random.randint(60000, 90000),
        "prev_cpu": round(random.uniform(20, 55), 2),
        "prev_memory": round(random.uniform(30, 65), 2),
        "prev_retries": random.randint(0, 1),
        "runtime_avg_last_5": round(random.uniform(120, 250), 2),
        "rows_avg_last_5": random.randint(60000, 90000),
        "retry_sum_last_5": random.randint(0, 2),
        "failure_count_last_5": 0,
        "sla_breach_count_last_5": 0,
    }


def run_sales_pipeline():
    metrics = generate_pipeline_metrics()

    prediction_response = requests.post(
        PREDICT_RISK_API_URL,
        json=metrics,
        timeout=10,
    )
    prediction_response.raise_for_status()
    prediction = prediction_response.json()

    pipeline_status = "WARNING" if prediction["risk_level"] == "HIGH" else "SUCCESS"

    pipeline_run_payload = {
        "pipeline_name": "sales_etl",
        "runtime_seconds": metrics["prev_runtime"],
        "rows_processed": metrics["prev_rows"],
        "cpu_usage": metrics["prev_cpu"],
        "memory_usage": metrics["prev_memory"],
        "retries": metrics["prev_retries"],
        "status": pipeline_status,
        "failure_risk_score": prediction["failure_risk_score"],
        "risk_level": prediction["risk_level"],
    }

    pipeline_run_response = requests.post(
        PIPELINE_RUN_API_URL,
        json=pipeline_run_payload,
        timeout=10,
    )
    pipeline_run_response.raise_for_status()

    print("Pipeline executed at:", datetime.now())
    print("Input metrics:", metrics)
    print("Prediction response:", prediction)
    print("Pipeline run stored:", pipeline_run_response.json())


with DAG(
    dag_id="sales_etl_dag",
    start_date=datetime(2025, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["predictops", "etl", "ml-monitoring"],
) as dag:

    run_pipeline = PythonOperator(
        task_id="run_sales_pipeline",
        python_callable=run_sales_pipeline,
    )
