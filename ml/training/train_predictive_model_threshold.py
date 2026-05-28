import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

DB_USER = "postgres"
DB_PASSWORD = "Nfb5%kia"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "predictops"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

df = pd.read_sql("SELECT * FROM pipeline_predictive_features", engine)

features = [
    "prev_runtime",
    "prev_rows",
    "prev_cpu",
    "prev_memory",
    "prev_retries",
    "runtime_avg_last_5",
    "rows_avg_last_5",
    "retry_sum_last_5",
    "failure_count_last_5",
    "sla_breach_count_last_5"
]

X = df[features]
y = df["next_failed"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight={0: 1, 1: 15},
    max_depth=8
)

model.fit(X_train, y_train)

probs = model.predict_proba(X_test)[:, 1]

threshold = 0.70
y_pred = (probs >= threshold).astype(int)

print("Threshold:", threshold)
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

joblib.dump(model, "ml/models/predictive_failure_model_threshold.pkl")

print("\nModel saved to ml/models/predictive_failure_model_threshold.pkl")
