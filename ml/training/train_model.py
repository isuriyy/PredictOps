import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

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

df = pd.read_sql("SELECT * FROM pipeline_features", engine)

features = [
    "runtime_sec",
    "rows_processed",
    "cpu_usage",
    "memory_usage",
    "retries",
    "runtime_rolling_avg",
    "rows_rolling_avg",
    "retry_rolling_sum",
    "cpu_memory_pressure"
]

X = df[features]
y = df["failed"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

joblib.dump(model, "ml/models/failure_prediction_model.pkl")

print("\nModel saved to ml/models/failure_prediction_model.pkl")
