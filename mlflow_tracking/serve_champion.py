import mlflow
import mlflow.sklearn
import pandas as pd

CHAMPION_ALIAS = "champion"
MODEL_NAME = "PredictOpsFailureClassifier"

def load_champion_model():
    client = mlflow.tracking.MlflowClient()
    version = client.get_model_version_by_alias(MODEL_NAME, CHAMPION_ALIAS)
    print(f"Loading {MODEL_NAME} version {version.version} (alias: {CHAMPION_ALIAS})")
    print(f"Run ID: {version.run_id}")
    model = mlflow.sklearn.load_model(version.source)
    return model

def predict(model, input_dict):
    df = pd.DataFrame([input_dict])
    prediction = model.predict(df)
    proba = model.predict_proba(df)
    return {
        "prediction": int(prediction[0]),
        "failure_probability": round(float(proba[0][1]), 4)
    }

if __name__ == "__main__":
    model = load_champion_model()

    sample = {
        "prev_runtime": 120, "prev_rows": 50000, "prev_cpu": 75,
        "prev_memory": 60, "prev_retries": 1, "runtime_avg_last_5": 115,
        "rows_avg_last_5": 48000, "retry_sum_last_5": 2,
        "failure_count_last_5": 1, "sla_breach_count_last_5": 1,
        "runtime_ratio": 1.04, "rows_ratio": 1.04, "cpu_memory_pressure": 4500,
        "retry_rate_last_5": 0.2, "failure_rate_last_5": 0.1,
        "sla_breach_rate_last_5": 0.1, "runtime_cpu_interaction": 9000,
        "runtime_memory_interaction": 7200, "retry_failure_interaction": 1,
        "retry_sla_interaction": 1
    }

    result = predict(model, sample)
    print(f"Prediction: {result['prediction']}")
    print(f"Failure Probability: {result['failure_probability']}")
