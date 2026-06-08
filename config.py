import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "predictops")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "ml/models/predictive_failure_model_threshold.pkl"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "PredictOpsFailureClassifier"
)

MODEL_ALIAS = os.getenv(
    "MODEL_ALIAS",
    "champion"
)

HIGH_RISK_THRESHOLD = float(os.getenv("HIGH_RISK_THRESHOLD", "0.70"))
MEDIUM_RISK_THRESHOLD = float(os.getenv("MEDIUM_RISK_THRESHOLD", "0.40"))
