import random
import time
import requests

URL = "http://127.0.0.1:8000/predict-risk"

while True:

    high_risk = random.choice([True, False, False])

    if high_risk:
        payload = {
            "prev_runtime": 520,
            "prev_rows": 45000,
            "prev_cpu": 88,
            "prev_memory": 91,
            "prev_retries": 3,
            "runtime_avg_last_5": 470,
            "rows_avg_last_5": 60000,
            "retry_sum_last_5": 9,
            "failure_count_last_5": 1,
            "sla_breach_count_last_5": 3
        }

    else:
        payload = {
            "prev_runtime": 120,
            "prev_rows": 70000,
            "prev_cpu": 30,
            "prev_memory": 40,
            "prev_retries": 0,
            "runtime_avg_last_5": 110,
            "rows_avg_last_5": 72000,
            "retry_sum_last_5": 0,
            "failure_count_last_5": 0,
            "sla_breach_count_last_5": 0
        }

    response = requests.post(URL, json=payload)

    print(response.json())

    time.sleep(10)
