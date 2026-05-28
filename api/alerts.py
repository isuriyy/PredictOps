import requests
from config import SLACK_WEBHOOK_URL


def send_high_risk_alert(risk_score, metrics):
    if not SLACK_WEBHOOK_URL:
        print("Slack webhook URL missing. Alert skipped.")
        return False

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

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message, timeout=5)
        print("Slack alert sent:", response.status_code)
        return response.status_code == 200
    except requests.RequestException as e:
        print("Slack alert failed:", e)
        return False
