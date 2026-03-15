-- Migration: 001_feature_registry.sql
-- Rule #11: Give feature columns owners and documentation
-- Rule #16: Plan to launch and iterate (easy to add/remove features)
-- Rule #22: Clean up features you are no longer using

CREATE TABLE IF NOT EXISTS feature_registry (
    id                   SERIAL PRIMARY KEY,
    feature_name         TEXT        NOT NULL UNIQUE,
    feature_type         TEXT        NOT NULL CHECK (feature_type IN ('NUMERIC', 'CATEGORICAL', 'EMBEDDING')),
    status               TEXT        NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'EXPERIMENTAL', 'DEPRECATED')),
    owner_email          TEXT        NOT NULL,
    backup_owner_email   TEXT,
    description          TEXT        NOT NULL,
    expected_coverage_pct FLOAT      NOT NULL DEFAULT 1.0 CHECK (expected_coverage_pct BETWEEN 0.0 AND 1.0),
    model_version        TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast status lookups (Rule #22: prune DEPRECATED features weekly)
CREATE INDEX IF NOT EXISTS idx_feature_registry_status
    ON feature_registry (status);

-- Index for owner lookups (Rule #11: accountability)
CREATE INDEX IF NOT EXISTS idx_feature_registry_owner
    ON feature_registry (owner_email);

-- Seed initial MLAOS features
INSERT INTO feature_registry
    (feature_name, feature_type, status, owner_email, backup_owner_email, description, expected_coverage_pct, model_version)
VALUES
    ('resonance_score',      'NUMERIC',     'ACTIVE',       'kennydallmier@gmail.com', NULL, 'Normalized resonance signal (0.0-1.0). Rule #17: directly observed.', 1.0, 'AURELIA-v2.3'),
    ('impedance_magnitude',  'NUMERIC',     'ACTIVE',       'kennydallmier@gmail.com', NULL, 'EIS impedance magnitude in Ohms. Rule #17: directly observed.',       1.0, 'AURELIA-v2.3'),
    ('hrv_score',            'NUMERIC',     'ACTIVE',       'kennydallmier@gmail.com', NULL, 'Heart rate variability score in ms. Rule #17: directly observed.',     1.0, 'AURELIA-v2.3'),
    ('chiaroscuro_index',    'NUMERIC',     'ACTIVE',       'kennydallmier@gmail.com', NULL, 'Synthetic feature: abs(light-dark)/(light+dark). Rule #20.',            0.95, 'AURELIA-v2.3'),
    ('sigma7_alignment',     'NUMERIC',     'ACTIVE',       'kennydallmier@gmail.com', NULL, 'Cosine similarity of sigma7 identity vs memory vector. Rule #32.',     0.90, 'AURELIA-v2.3'),
    ('light_intensity',      'NUMERIC',     'ACTIVE',       'kennydallmier@gmail.com', NULL, 'Raw light intensity sensor reading. Rule #17: directly observed.',     1.0, 'AURELIA-v2.3'),
    ('dark_intensity',       'NUMERIC',     'ACTIVE',       'kennydallmier@gmail.com', NULL, 'Raw dark intensity sensor reading. Rule #17: directly observed.',      1.0, 'AURELIA-v2.3')
ON CONFLICT (feature_name) DO NOTHING;
