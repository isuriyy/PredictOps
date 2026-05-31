import joblib
import pandas as pd
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from config import (
    DATABASE_URL,
    MODEL_PATH,
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD,
)

from api.alerts import send_high_risk_alert


app = FastAPI(title="PredictOps API")

model = joblib.load(MODEL_PATH)
engine = create_engine(DATABASE_URL)
templates = Jinja2Templates(directory="api/templates")
total_predictions_gauge = Gauge("predictops_total_predictions", "Total recent predictions")
high_risk_gauge = Gauge("predictops_high_risk_count", "High risk prediction count")
medium_risk_gauge = Gauge("predictops_medium_risk_count", "Medium risk prediction count")
low_risk_gauge = Gauge("predictops_low_risk_count", "Low risk prediction count")
average_risk_score_gauge = Gauge("predictops_average_risk_score", "Average failure risk score")

average_runtime_gauge = Gauge(
    "predictops_average_runtime",
    "Average previous pipeline runtime"
)
pipeline_runtime_gauge = Gauge(
    "predictops_pipeline_runtime_seconds",
    "Latest pipeline runtime in seconds"
)

pipeline_rows_gauge = Gauge(
    "predictops_pipeline_rows_processed",
    "Latest pipeline rows processed"
)

pipeline_retries_gauge = Gauge(
    "predictops_pipeline_retries",
    "Latest pipeline retry count"
)

pipeline_cpu_gauge = Gauge(
    "predictops_pipeline_cpu_usage",
    "Latest pipeline CPU usage"
)

pipeline_memory_gauge = Gauge(
    "predictops_pipeline_memory_usage",
    "Latest pipeline memory usage"
)

total_runs_gauge = Gauge(
    "predictops_total_runs",
    "Total historical pipeline runs"
)

success_runs_gauge = Gauge(
    "predictops_success_runs",
    "Successful historical pipeline runs"
)

warning_runs_gauge = Gauge(
    "predictops_warning_runs",
    "Warning historical pipeline runs"
)

avg_runtime_gauge = Gauge(
    "predictops_avg_runtime_seconds",
    "Average historical pipeline runtime in seconds"
)

avg_cpu_gauge = Gauge(
    "predictops_avg_cpu_usage",
    "Average historical CPU usage"
)

avg_memory_gauge = Gauge(
    "predictops_avg_memory_usage",
    "Average historical memory usage"
)

avg_retries_gauge = Gauge(
    "predictops_avg_retries",
    "Average historical retry count"
)


class PipelineMetrics(BaseModel):
    prev_runtime: float
    prev_rows: float
    prev_cpu: float
    prev_memory: float
    prev_retries: int
    runtime_avg_last_5: float
    rows_avg_last_5: float
    retry_sum_last_5: int
    failure_count_last_5: int
    sla_breach_count_last_5: int

class PipelineRun(BaseModel):
    pipeline_name: str
    runtime_seconds: float
    rows_processed: int
    cpu_usage: float
    memory_usage: float
    retries: int
    status: str
    failure_risk_score: float | None = None
    risk_level: str | None = None

@app.get("/")
def home():
    return {"message": "PredictOps API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PredictOps API",
        "model_loaded": model is not None,
    }


@app.post("/predict-risk")
def predict_risk(metrics: PipelineMetrics):
    input_data = metrics.model_dump()
    df = pd.DataFrame([input_data])

    risk_score = model.predict_proba(df)[0][1]

    if risk_score >= HIGH_RISK_THRESHOLD:
        risk_level = "HIGH"
    elif risk_score >= MEDIUM_RISK_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if risk_level == "HIGH":
        send_high_risk_alert(risk_score, input_data)

    prediction_record = input_data.copy()
    prediction_record["prediction_time"] = datetime.now()
    prediction_record["failure_risk_score"] = round(float(risk_score), 3)
    prediction_record["risk_level"] = risk_level

    pd.DataFrame([prediction_record]).to_sql(
        "prediction_logs",
        engine,
        if_exists="append",
        index=False,
    )

    return {
        "failure_risk_score": round(float(risk_score), 3),
        "risk_level": risk_level,
        "logged": True,
    }


@app.get("/prediction-logs")
def get_prediction_logs(limit: int = 10):
    query = f"""
    SELECT *
    FROM prediction_logs
    ORDER BY prediction_time DESC
    LIMIT {limit}
    """

    df = pd.read_sql(query, engine)
    
    return df.to_dict(orient="records")

@app.get("/pipeline-history")
def get_pipeline_history(limit: int = 20):
    query = f"""
    SELECT
        id,
        pipeline_name,
        run_time,
        runtime_seconds,
        rows_processed,
        cpu_usage,
        memory_usage,
        retries,
        status,
        failure_risk_score,
        risk_level
    FROM pipeline_runs
    ORDER BY run_time DESC
    LIMIT {limit}
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@app.post("/pipeline-run")
def create_pipeline_run(run: PipelineRun):
    record = run.model_dump()
    record["run_time"] = datetime.now()

    pd.DataFrame([record]).to_sql(
        "pipeline_runs",
        engine,
        if_exists="append",
        index=False
    )

    return {
        "message": "Pipeline run stored",
        "pipeline_name": record["pipeline_name"],
        "status": record["status"],
        "risk_level": record["risk_level"]
    }

@app.get("/pipeline-analytics")
def get_pipeline_analytics():
    df = pd.read_sql(
        "SELECT * FROM pipeline_runs",
        engine,
    )

    if df.empty:
        return {
            "total_runs": 0,
            "success_runs": 0,
            "warning_runs": 0,
            "average_runtime_seconds": 0,
            "average_rows_processed": 0,
            "average_cpu_usage": 0,
            "average_memory_usage": 0,
            "average_retries": 0,
            "high_risk_runs": 0,
            "low_risk_runs": 0,
        }

    return {
        "total_runs": int(len(df)),
        "success_runs": int(len(df[df["status"] == "SUCCESS"])),
        "warning_runs": int(len(df[df["status"] == "WARNING"])),
        "average_runtime_seconds": round(float(df["runtime_seconds"].mean()), 2),
        "average_rows_processed": round(float(df["rows_processed"].mean()), 2),
        "average_cpu_usage": round(float(df["cpu_usage"].mean()), 2),
        "average_memory_usage": round(float(df["memory_usage"].mean()), 2),
        "average_retries": round(float(df["retries"].mean()), 2),
        "high_risk_runs": int(len(df[df["risk_level"] == "HIGH"])),
        "low_risk_runs": int(len(df[df["risk_level"] == "LOW"])),
    }

@app.get("/metrics-summary")
def metrics_summary():
    df = pd.read_sql(
        "SELECT * FROM prediction_logs ORDER BY prediction_time DESC LIMIT 50",
        engine,
    )

    if df.empty:
        return {
            "total_predictions": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "average_risk_score": 0,
        }

    return {
        "total_predictions": len(df),
        "high_risk_count": len(df[df["risk_level"] == "HIGH"]),
        "medium_risk_count": len(df[df["risk_level"] == "MEDIUM"]),
        "low_risk_count": len(df[df["risk_level"] == "LOW"]),
        "average_risk_score": round(float(df["failure_risk_score"].mean()), 3),
    }

@app.get("/metrics")
def prometheus_metrics():
    df = pd.read_sql(
        "SELECT * FROM prediction_logs ORDER BY prediction_time DESC LIMIT 50",
        engine,
    )

    if df.empty:
        total_predictions_gauge.set(0)
        high_risk_gauge.set(0)
        medium_risk_gauge.set(0)
        low_risk_gauge.set(0)
        average_risk_score_gauge.set(0)
        average_runtime_gauge.set(0)
    else:
        total_predictions_gauge.set(len(df))
        high_risk_gauge.set(len(df[df["risk_level"] == "HIGH"]))
        medium_risk_gauge.set(len(df[df["risk_level"] == "MEDIUM"]))
        low_risk_gauge.set(len(df[df["risk_level"] == "LOW"]))
        average_risk_score_gauge.set(float(df["failure_risk_score"].mean()))
        average_runtime_gauge.set(float(df["prev_runtime"].mean()))

    pipeline_df = pd.read_sql(
        "SELECT * FROM pipeline_runs ORDER BY run_time DESC LIMIT 1",
        engine,
    )

    if pipeline_df.empty:
        pipeline_runtime_gauge.set(0)
        pipeline_rows_gauge.set(0)
        pipeline_retries_gauge.set(0)
        pipeline_cpu_gauge.set(0)
        pipeline_memory_gauge.set(0)
    else:
        latest_run = pipeline_df.iloc[0]

        pipeline_runtime_gauge.set(float(latest_run["runtime_seconds"]))
        pipeline_rows_gauge.set(float(latest_run["rows_processed"]))
        pipeline_retries_gauge.set(float(latest_run["retries"]))
        pipeline_cpu_gauge.set(float(latest_run["cpu_usage"]))
        pipeline_memory_gauge.set(float(latest_run["memory_usage"]))

    analytics_df = pd.read_sql(
        "SELECT * FROM pipeline_runs",
        engine,
    )

    if analytics_df.empty:
        total_runs_gauge.set(0)
        success_runs_gauge.set(0)
        warning_runs_gauge.set(0)
        avg_runtime_gauge.set(0)
        avg_cpu_gauge.set(0)
        avg_memory_gauge.set(0)
        avg_retries_gauge.set(0)
    else:
        total_runs_gauge.set(len(analytics_df))
        success_runs_gauge.set(len(analytics_df[analytics_df["status"] == "SUCCESS"]))
        warning_runs_gauge.set(len(analytics_df[analytics_df["status"] == "WARNING"]))
        avg_runtime_gauge.set(float(analytics_df["runtime_seconds"].mean()))
        avg_cpu_gauge.set(float(analytics_df["cpu_usage"].mean()))
        avg_memory_gauge.set(float(analytics_df["memory_usage"].mean()))
        avg_retries_gauge.set(float(analytics_df["retries"].mean()))


    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    df = pd.read_sql(
        "SELECT * FROM prediction_logs ORDER BY prediction_time DESC LIMIT 50",
        engine,
    )

    total_predictions = len(df)
    high_risk_count = len(df[df["risk_level"] == "HIGH"])
    medium_risk_count = len(df[df["risk_level"] == "MEDIUM"])
    low_risk_count = len(df[df["risk_level"] == "LOW"])

    logs = df.to_dict(orient="records")

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "logs": logs,
            "total_predictions": total_predictions,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count,
        },
    )
