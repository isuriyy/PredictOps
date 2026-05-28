import joblib
import pandas as pd

MODEL_PATH = "ml/models/predictive_failure_model_threshold.pkl"

model = joblib.load(MODEL_PATH)

sample = pd.DataFrame([{
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
}])

risk_score = model.predict_proba(sample)[0][1]

if risk_score >= 0.70:
    risk_level = "HIGH"
elif risk_score >= 0.40:
    risk_level = "MEDIUM"
else:
    risk_level = "LOW"

print("Failure risk score:", round(risk_score, 3))
print("Risk level:", risk_level)
