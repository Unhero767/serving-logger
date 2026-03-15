-- Serving Logs Schema (Rule #29: Log features at serving time)
-- Author: Kenneth Dallmier | kennydallmier@gmail.com
-- Repository: serving-logger

CREATE TABLE IF NOT EXISTS serving_logs (
    log_id          BIGSERIAL PRIMARY KEY,
    request_id      UUID NOT NULL,
    memory_id       VARCHAR(255) NOT NULL,
    feature_name    VARCHAR(255) NOT NULL,
    feature_value   JSONB NOT NULL,
    model_version   VARCHAR(100) NOT NULL,
    logged_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    environment     VARCHAR(20) NOT NULL DEFAULT 'production'
                        CHECK (environment IN ('production', 'staging', 'development'))
);

CREATE INDEX idx_serving_logs_request ON serving_logs(request_id);
CREATE INDEX idx_serving_logs_feature ON serving_logs(feature_name);
CREATE INDEX idx_serving_logs_logged_at ON serving_logs(logged_at);
CREATE INDEX idx_serving_logs_model_version ON serving_logs(model_version);
CREATE INDEX idx_serving_logs_env ON serving_logs(environment);

-- Retention policy: auto-clean logs older than 90 days
-- (Run this manually or via scheduled job)
-- DELETE FROM serving_logs WHERE logged_at < NOW() - INTERVAL '90 days';

-- Skew analysis view (Rule #37)
CREATE OR REPLACE VIEW skew_analysis_view AS
SELECT
    feature_name,
    model_version,
    COUNT(*) as sample_count,
    AVG((feature_value->>'value')::FLOAT) as avg_serving_value,
    STDDEV((feature_value->>'value')::FLOAT) as stddev_serving_value,
    MIN(logged_at) as first_seen,
    MAX(logged_at) as last_seen
FROM serving_logs
WHERE environment = 'production'
  AND logged_at > NOW() - INTERVAL '7 days'
  AND jsonb_typeof(feature_value->'value') = 'number'
GROUP BY feature_name, model_version
ORDER BY feature_name, model_version;
