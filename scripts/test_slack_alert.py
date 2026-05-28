import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from api.alerts import send_high_risk_alert

metrics = {
    "prev_runtime": 520,
    "prev_cpu": 88,
    "prev_memory": 91,
    "prev_retries": 3,
    "sla_breach_count_last_5": 3
}

send_high_risk_alert(0.967, metrics)
