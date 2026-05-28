import os
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
from datetime import datetime

from config import DATABASE_URL, MODEL_PATH, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from api.alerts import send_high_risk_alert
from dotenv import load_dotenv

app = FastAPI(title="PredictOps API")

model = joblib.load("ml/models/predictive_failure_model_threshold.pkl")

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
templates = Jinja2Templates(directory="api/templates")
model = joblib.load(MODEL_PATH)
engine = create_engine(DATABASE_URL)

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

@app.post("/predict-risk")
def predict_risk(metrics: PipelineMetrics):
    input_data = metrics.model_dump()
    df = pd.DataFrame([input_data])

    risk_score = model.predict_proba(df)[0][1]

    if risk_score >= 0.70:
        risk_level = "HIGH"
    elif risk_score >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if risk_score >= 0.70:
        send_high_risk_alert(risk_score, input_data)

    if risk_score >= HIGH_RISK_THRESHOLD:
        risk_level = "HIGH"
    elif risk_score >= MEDIUM_RISK_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    prediction_record = input_data.copy()
    prediction_record["prediction_time"] = datetime.now()
    prediction_record["failure_risk_score"] = round(float(risk_score), 3)
    prediction_record["risk_level"] = risk_level

    pd.DataFrame([prediction_record]).to_sql(
        "prediction_logs",
        engine,
        if_exists="append",
        index=False
    )

    return {
        "failure_risk_score": round(float(risk_score), 3),
        "risk_level": risk_level,
        "logged": True
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

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    df = pd.read_sql(
        "SELECT * FROM prediction_logs ORDER BY prediction_time DESC LIMIT 50",
        engine
    )

    total_predictions = len(df)
    high_risk_count = len(df[df["risk_level"] == "HIGH"])
    medium_risk_count = len(df[df["risk_level"] == "MEDIUM"])
    low_risk_count = len(df[df["risk_level"] == "LOW"])

    logs = df.to_dict(orient="records")

    context = {
        "request": request,
        "logs": logs,
        "total_predictions": total_predictions,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
    }

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "logs": logs,
            "total_predictions": total_predictions,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count,
    }
)