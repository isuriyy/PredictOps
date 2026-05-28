# PredictOps

PredictOps is a predictive data pipeline reliability platform that uses machine learning to estimate near-future pipeline failure risk before failures happen.

The system simulates pipeline execution logs, stores them in PostgreSQL, builds predictive features, serves risk predictions through FastAPI, logs prediction results, displays them in a dashboard, and sends Slack alerts for high-risk pipeline states.

## Problem

Traditional monitoring tells teams when a service or database is down. It does not always warn teams when a healthy-looking data pipeline is becoming unstable.

PredictOps focuses on predictive reliability by identifying early signs of pipeline instability before upcoming pipeline failures occur.

## Key Features

* Synthetic pipeline telemetry generation
* PostgreSQL-based operational metadata storage
* Predictive feature engineering
* Machine learning failure-risk prediction
* FastAPI prediction API
* Prediction logging to PostgreSQL
* HTML dashboard for recent predictions
* Slack alerts for high-risk predictions
* Dockerized API and PostgreSQL stack

## Architecture

```text
Synthetic Pipeline Logs
        ↓
PostgreSQL
        ↓
Feature Engineering
        ↓
ML Failure Risk Model
        ↓
FastAPI Prediction API
        ↓
Prediction Logs
        ↓
Dashboard + Slack Alerts
```

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Pandas
* Scikit-learn
* Docker
* Jinja2
* Slack Webhooks

## API Endpoints

| Method | Endpoint           | Description                   |
| ------ | ------------------ | ----------------------------- |
| GET    | `/`                | API health check              |
| POST   | `/predict-risk`    | Predict pipeline failure risk |
| GET    | `/prediction-logs` | View recent prediction logs   |
| GET    | `/dashboard`       | Open prediction dashboard     |

## Example Prediction Request

```json
{
  "prev_runtime": 520,
  "prev_rows": 45000,
  "prev_cpu": 88,
  "prev_memory": 91,
  "prev_retries": 3,
  "runtime_avg_last_5": 470,
  "rows_avg_last_5": 60000,
  "retry_sum_last_5": 9,
  "failure_count_last_5": 1,
  "sla_breach_count_last_5": 3
}
```

## Example Response

```json
{
  "failure_risk_score": 0.967,
  "risk_level": "HIGH",
  "logged": true
}
```

## Running the Project with Docker

Create a `.env` file in the project root:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
DB_NAME=predictops
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

Run the system:

```bash
docker compose up --build
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

Open the dashboard:

```text
http://127.0.0.1:8000/dashboard
```

## Database Setup

The Docker Compose setup includes a PostgreSQL container. Pipeline logs and predictive features can be loaded using the project scripts.

For local loading into the Docker PostgreSQL container, use:

```env
DB_HOST=localhost
DB_PORT=5433
```

Then run:

```bash
python scripts/generate_logs.py
python scripts/load_to_postgres.py
python ml/training/build_predictive_features.py
```

## Model Baseline

The current model is a Random Forest classifier trained on predictive pipeline features.

Target:

```text
Predict whether a pipeline is likely to fail within the next few runs.
```

Current baseline:

```text
Threshold: 0.70
Class 1 precision: 0.32
Class 1 recall: 0.44
Class 1 F1-score: 0.37
```

This is an initial baseline and will be improved with richer operational patterns, better feature engineering, and real orchestration logs.

## Future Improvements

* Add Airflow DAG orchestration
* Add MLflow experiment tracking
* Add automated model retraining
* Add Prometheus/Grafana monitoring
* Add authentication
* Add CI/CD pipeline
* Deploy to cloud
* Use real pipeline execution logs

## Screenshots

### Swagger API
![Swagger API](dashboard/03_swagger_api.png)

### Dashboard
![Dashboard](dashboard/01_Dashboard.png)

### Slack Alert Integration
![Slack Alert](dashboard/02_Slack_Alerts.png)

### Dockerized Deployment
![Docker Containers](dashboard/04_Docker_containers.png)


## Project Status

PredictOps currently supports end-to-end ML risk prediction, API serving, PostgreSQL logging, dashboard visualization, Slack alerting, and Dockerized execution.

