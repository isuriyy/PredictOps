CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    run_time TIMESTAMP NOT NULL,
    runtime_seconds FLOAT NOT NULL,
    rows_processed INTEGER NOT NULL,
    cpu_usage FLOAT NOT NULL,
    memory_usage FLOAT NOT NULL,
    retries INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    failure_risk_score FLOAT,
    risk_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
