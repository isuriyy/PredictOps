# PredictOps

PredictOps is a predictive data pipeline reliability platform that uses machine learning to estimate near-future pipeline failure risk before failures happen.

The system simulates pipeline execution logs, stores them in PostgreSQL, builds predictive features, serves risk predictions through FastAPI, logs prediction results, displays them in a dashboard, and sends Slack alerts for high-risk pipeline states.

## Problem

Traditional monitoring tells teams when a service or database is down. It does not always warn teams when a healthy-looking data pipeline is becoming unstable.

PredictOps focuses on predictive reliability by identifying early signs of pipeline instability before upcoming pipeline failures occur.

## Key Features

* Synthetic pipeline telemetry generation
* PostgreSQL operational metadata storage
* Predictive feature engineering
* Machine learning failure-risk prediction
* FastAPI prediction API
* Prediction logging and analytics
* Airflow ETL orchestration
* Prometheus metrics collection
* Grafana monitoring dashboards
* Grafana alert management
* Discord alert notifications
* Runtime SLA monitoring
* Resource utilization monitoring
* AI risk analytics dashboard
* Dockerized deployment

## Architecture

Synthetic Pipeline Logs
          ↓
      PostgreSQL
          ↓
 Feature Engineering
          ↓
  ML Risk Prediction
          ↓
      FastAPI API
          ↓
   Prediction Logs
          ↓
     Airflow DAG
          ↓
 Prometheus Metrics
          ↓
 Grafana Dashboards
          ↓
 Alert Rules Engine
          ↓
 Discord Notifications


## Tech Stack

### Data Engineering
* Apache Airflow
* PostgreSQL
* Docker

### Machine Learning
* Scikit-learn
* Pandas
* NumPy

### Backend
* FastAPI
* SQLAlchemy

### Monitoring
* Prometheus
* Grafana

### Alerting
* Grafana Alerting
* Discord Webhooks

### Visualization
* Grafana Dashboards
* Jinja2


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

* MLflow experiment tracking
* Automated model retraining
* Model registry
* Drift detection
* CI/CD pipeline
* Kubernetes deployment
* Cloud deployment (AWS/Azure/GCP)
* Real production pipeline logs


## Monitoring & Alerting

PredictOps includes a complete observability layer.

### Airflow
- ETL orchestration
- Scheduled pipeline execution
- Runtime tracking

### Prometheus
- Runtime metrics
- Resource metrics
- Risk prediction metrics
- Pipeline health metrics

### Grafana
- Executive dashboards
- Pipeline performance monitoring
- Resource monitoring
- AI risk analytics

### Alerting
- High Risk Prediction Alert
- Runtime SLA Alert
- CPU Usage Alert
- Memory Usage Alert
- Failure Risk Score Alert

### Discord Notifications

Real-time notifications are automatically sent when:

- Pipeline runtime exceeds SLA
- Memory usage exceeds threshold
- CPU usage exceeds threshold
- Failure risk becomes critical

Resolved alerts are also automatically sent.


## Screenshots

### Swagger API
![Swagger API](dashboard/03_swagger_api.png)

### Dashboard
![Dashboard](dashboard/01_Dashboard.png)

### Slack Alert Integration
![Slack Alert](dashboard/02_Slack_Alerts.png)

### Dockerized Deployment
![Docker Containers](dashboard/04_Docker_containers.png)

## Monitoring Dashboard

### Grafana Dashboard
![Grafana Dashboard](dashboard/05_Grafana_Dashboard_1.png)

### Risk Distribution
![Grafana Dashboard](dashboard/06_Grafana_Dashboard_2.png)

### Prometheus Targets
![Prometheus Targets](dashboard/07_Prometheus_Targets.png)

### Prometheus Metrics
![Prometheus Metrics](dashboard/08_Prometheus_Metrics.png)

### API Health Endpoint
![API Health](dashboard/09_API_Health.png)

### Metrics Endpoint
![Metrics Endpoint](dashboard/09_Prometheus_Metrics_Endpoint.png)

### Docker Containers
![Docker Containers](dashboard/11_Docker_Containers.png)

## Screenshots

### Airflow DAG Overview
![Airflow DAG](dashboard/airflow_dag_overview.png)

### Airflow Execution History
![Airflow Runs](dashboard/airflow_execution_history.png)

### Prometheus Metrics Query
![Prometheus](dashboard/prometheus_query.png)

### Grafana Executive Dashboard
![Grafana Executive](dashboard/grafana_executive_dashboard.png)

### Grafana Pipeline Performance
![Pipeline Performance](dashboard/grafana_pipeline_performance.png)

### Grafana Resource Monitoring
![Resource Monitoring](dashboard/grafana_resource_monitoring.png)

### Grafana AI Analytics
![AI Analytics](dashboard/grafana_ai_analytics.png)

### Grafana Alert Rules
![Alert Rules](dashboard/grafana_alert_rules.png)

### Discord Alert Notification
![Discord Alert](dashboard/discord_high_risk_alert.png)

### Discord Alert Resolution
![Discord Resolution](dashboard/discord_alert_resolved.png)


## Project Status

PredictOps is a complete end-to-end predictive data reliability platform.

Current capabilities:

✅ Machine learning failure prediction

✅ FastAPI prediction service

✅ PostgreSQL operational data storage

✅ Airflow ETL orchestration

✅ Prometheus metrics collection

✅ Grafana dashboards

✅ Grafana alert management

✅ Discord alert notifications

✅ Dockerized deployment

Next milestone:

🚀 MLflow experiment tracking and model lifecycle management

