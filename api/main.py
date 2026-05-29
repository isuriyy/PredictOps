import joblib
import pandas as pd
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine

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

@app.get("/metrics-summary")
def metrics_summary():
    df = pd.read_sql(
        "SELECT * FROM prediction_logs ORDER BY prediction_time DESC LIMIT 50",
        engine,
    )

    return {
        "total_predictions": len(df),
        "high_risk_count": len(df[df["risk_level"] == "HIGH"]),
        "medium_risk_count": len(df[df["risk_level"] == "MEDIUM"]),
        "low_risk_count": len(df[df["risk_level"] == "LOW"]),
        "average_risk_score": round(float(df["failure_risk_score"].mean()), 3)
        if not df.empty
        else 0,
    }

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
