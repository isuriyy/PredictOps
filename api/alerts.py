import os
from pathlib import Path
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_high_risk_alert(risk_score, metrics):
    if not SLACK_WEBHOOK_URL:
        print("Slack webhook URL is missing. Alert not sent.")
        return

    message = {
        "text": (
            f"🚨 PredictOps HIGH-RISK ALERT\n\n"
            f"Risk Score: {risk_score:.3f}\n"
            f"Runtime: {metrics['prev_runtime']}\n"
            f"CPU Usage: {metrics['prev_cpu']}%\n"
            f"Memory Usage: {metrics['prev_memory']}%\n"
            f"Retries: {metrics['prev_retries']}\n"
            f"SLA Breaches: {metrics['sla_breach_count_last_5']}"
        )
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    print("Slack alert sent:", response.status_code)
