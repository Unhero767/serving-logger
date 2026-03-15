-- =============================================================
-- sql/feature_registry.sql
-- Feature Registry Schema + Seed Data
--
-- Glossary Alignment (Google ML Glossary):
--   feature        : An input variable to a machine learning model
--   feature column : A set of related features (Google TF terminology)
--   categorical    : Features with a specific set of possible values
--   numerical      : Features represented as integers or real-valued numbers
--   coverage       : How many examples have a non-missing value for this feature
--   feature engineering : Converting raw data into useful features
--
-- Rules Compliance:
--   Rule #11 : Give feature columns owners and documentation
--   Rule #22 : Clean up features you are no longer using
--   Rule #29 : Log features at serving time (referenced via feature_name FK)
-- =============================================================

-- ---------------------------------------------------------------
-- TABLE: feature_registry
-- Central registry of all MLAOS features with ownership and docs.
-- Rule #11: Every feature column must have an owner and description.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feature_registry (
    -- Primary key
    feature_id          SERIAL          PRIMARY KEY,

    -- Glossary: "feature" - an input variable to a machine learning model
    feature_name        VARCHAR(128)    NOT NULL UNIQUE,

    -- Rule #11: Owner of this feature column (must be a real person)
    owner_email         VARCHAR(256)    NOT NULL,

    -- Glossary: "feature engineering" - description of how raw data
    -- is transformed into this feature
    description         TEXT            NOT NULL,

    -- Glossary: "categorical data" | "numerical data" | "synthetic"
    -- categorical : finite set of possible values (e.g. status)
    -- numerical   : continuous or discrete numeric values
    -- synthetic   : assembled from one or more input features
    feature_type        VARCHAR(32)     NOT NULL
                        CHECK (feature_type IN ('numerical', 'categorical', 'synthetic', 'embedding')),

    -- Glossary: "continuous feature" vs "discrete feature"
    value_range         VARCHAR(128)    NULL,  -- e.g. '[0.0, 1.0]' or 'ACTIVE|EXPERIMENTAL|DEPRECATED'

    -- Rule #22: Expected coverage (0.0-1.0) - what fraction of examples
    -- should have a non-missing value for this feature
    expected_coverage   NUMERIC(5, 4)   NOT NULL
                        CHECK (expected_coverage >= 0.0 AND expected_coverage <= 1.0),

    -- Lifecycle management (Rule #22: deprecate unused features)
    status              VARCHAR(32)     NOT NULL DEFAULT 'ACTIVE'
                        CHECK (status IN ('ACTIVE', 'EXPERIMENTAL', 'DEPRECATED')),

    -- Source of raw data before feature engineering
    raw_source          VARCHAR(256)    NULL,

    -- For synthetic features: the formula or transformation applied
    -- Glossary: "synthetic feature" - assembled from one or more input features
    synthetic_formula   TEXT            NULL,

    -- Normalization method applied
    -- Glossary: "normalization" - converting variable's actual range to standard range
    normalization       VARCHAR(32)     NULL
                        CHECK (normalization IN ('min_max', 'zscore', 'none', NULL)),

    -- Audit columns
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deprecated_at       TIMESTAMPTZ     NULL,
    deprecated_reason   TEXT            NULL
);

-- Index for fast lookup by owner (Rule #11 queries)
CREATE INDEX IF NOT EXISTS idx_feature_registry_owner
    ON feature_registry (owner_email);

-- Index for status filtering (Rule #22: find deprecated features)
CREATE INDEX IF NOT EXISTS idx_feature_registry_status
    ON feature_registry (status);

-- Auto-update updated_at on row change
CREATE OR REPLACE FUNCTION update_feature_registry_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_feature_registry_updated_at
    BEFORE UPDATE ON feature_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_feature_registry_updated_at();


-- =============================================================
-- SEED DATA: MLAOS Feature Registry
-- All active features used by the MLAOS inference pipeline.
-- Owner: Kenneth Dallmier <kennydallmier@gmail.com> (Rule #11)
-- =============================================================

INSERT INTO feature_registry (
    feature_name,
    owner_email,
    description,
    feature_type,
    value_range,
    expected_coverage,
    status,
    raw_source,
    synthetic_formula,
    normalization
) VALUES

-- -----------------------------------------------------------
-- 1. resonance_score
--    Glossary: continuous feature, numerical data
--    Rule #11: owned, documented
--    Rule #29: logged via ServingLogger.log_inference()
-- -----------------------------------------------------------
(
    'resonance_score',
    'kennydallmier@gmail.com',
    'Normalized EIS resonance frequency score. Primary label signal for cognitive '
    'resonance state in MLAOS memory nodes. Derived from raw impedance spectroscopy '
    'measurement via min-max normalization over [0.0, 1.0]. '
    'Glossary: continuous feature (floating-point, infinite range within bounds), '
    'numerical data (real-valued number). Used as both input feature and label (0.0-1.0).',
    'numerical',
    '[0.0, 1.0]',
    0.9900,
    'ACTIVE',
    'eis_sensor.resonance_raw',
    NULL,
    'min_max'
),

-- -----------------------------------------------------------
-- 2. impedance_magnitude
--    Glossary: continuous feature, numerical data
--    Rule #11: owned, documented
-- -----------------------------------------------------------
(
    'impedance_magnitude',
    'kennydallmier@gmail.com',
    'Bioelectric impedance magnitude in ohms, normalized to [0.0, 1.0] via min-max '
    'over [0, 100 ohm] range. Captures tissue resistance state correlated with '
    'cognitive load in MLAOS EIS sensor array. '
    'Glossary: continuous feature, numerical data. '
    'Raw source: impedance_raw from EIS sensor pipeline.',
    'numerical',
    '[0.0, 1.0]',
    0.9500,
    'ACTIVE',
    'eis_sensor.impedance_raw',
    NULL,
    'min_max'
),

-- -----------------------------------------------------------
-- 3. chiaroscuro_index
--    Glossary: synthetic feature (assembled from light + dark intensity)
--    Rule #11: owned, documented with formula
-- -----------------------------------------------------------
(
    'chiaroscuro_index',
    'kennydallmier@gmail.com',
    'Synthetic feature: contrast ratio between photoreceptive light and dark '
    'channel intensities in the MLAOS visual cortex simulation. '
    'Formula: (light_intensity - dark_intensity) / (light_intensity + dark_intensity). '
    'Range [-1.0, 1.0]; positive = light-dominant, negative = dark-dominant. '
    'Glossary: synthetic feature (assembled from two input features), '
    'continuous feature. Named after chiaroscuro art technique (light/shadow contrast).',
    'synthetic',
    '[-1.0, 1.0]',
    0.9000,
    'ACTIVE',
    'visual_sensor.light_intensity, visual_sensor.dark_intensity',
    '(light_intensity - dark_intensity) / (light_intensity + dark_intensity)',
    'none'
),

-- -----------------------------------------------------------
-- 4. hrv_score
--    Glossary: continuous feature, numerical data
--    Rule #11: owned, documented
-- -----------------------------------------------------------
(
    'hrv_score',
    'kennydallmier@gmail.com',
    'Heart rate variability score from biometric sensor array. Passthrough feature '
    'representing autonomic nervous system state, correlated with cognitive arousal. '
    'Range [0.0, 1.0]; 1.0 = high variability (relaxed), 0.0 = low variability (stressed). '
    'Glossary: continuous feature, numerical data. No normalization applied '
    '(sensor already outputs normalized value). Rule #22: monitor coverage monthly.',
    'numerical',
    '[0.0, 1.0]',
    0.8500,
    'ACTIVE',
    'biometric_sensor.hrv_raw',
    NULL,
    'none'
),

-- -----------------------------------------------------------
-- 5. memory_vector_mean
--    Glossary: continuous feature, synthetic feature (mean reduction)
--    Rule #11: owned, documented
-- -----------------------------------------------------------
(
    'memory_vector_mean',
    'kennydallmier@gmail.com',
    'Mean of the MLAOS memory node embedding vector. Reduces the high-dimensional '
    'memory state vector to a scalar via arithmetic mean. Captures average activation '
    'level across all memory dimensions. '
    'Glossary: synthetic feature (assembled from memory_vector array via reduction), '
    'continuous feature, numerical data. '
    'Formula: sum(memory_vector) / len(memory_vector). '
    'Rule #32: identical reduction applied in training and serving pipelines.',
    'synthetic',
    '[0.0, 1.0]',
    0.9900,
    'ACTIVE',
    'mlaos_engine.memory_vector',
    'sum(memory_vector) / len(memory_vector)',
    'none'
),

-- -----------------------------------------------------------
-- 6. feature_status (categorical example)
--    Glossary: categorical data (finite set of possible values)
--    Rule #11: owned, documented
--    Rule #22: status field itself tracks feature lifecycle
-- -----------------------------------------------------------
(
    'node_status',
    'kennydallmier@gmail.com',
    'Operational status of the MLAOS memory node at inference time. '
    'Indicates whether the node is actively engaged, in experimental mode, '
    'or deprecated/inactive. '
    'Glossary: categorical data (features having a specific set of possible values): '
    'ACTIVE = node fully operational, '
    'EXPERIMENTAL = node under evaluation, '
    'DEPRECATED = node decommissioned, excluded from model input. '
    'Rule #22: nodes with DEPRECATED status should be cleaned up within 30 days.',
    'categorical',
    'ACTIVE|EXPERIMENTAL|DEPRECATED',
    0.9999,
    'ACTIVE',
    'mlaos_engine.node_registry.status',
    NULL,
    'none'
);


-- =============================================================
-- VIEWS: Feature Registry Operational Queries
-- =============================================================

-- Rule #11: All features by owner
CREATE OR REPLACE VIEW v_features_by_owner AS
SELECT
    owner_email,
    COUNT(*) AS total_features,
    SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_features,
    SUM(CASE WHEN status = 'DEPRECATED' THEN 1 ELSE 0 END) AS deprecated_features,
    ARRAY_AGG(feature_name ORDER BY feature_name) AS feature_names
FROM feature_registry
GROUP BY owner_email;

-- Rule #22: Features to clean up (deprecated but not yet removed)
CREATE OR REPLACE VIEW v_deprecated_features AS
SELECT
    feature_name,
    owner_email,
    deprecated_at,
    deprecated_reason,
    EXTRACT(DAY FROM NOW() - deprecated_at) AS days_since_deprecation
FROM feature_registry
WHERE status = 'DEPRECATED'
ORDER BY deprecated_at ASC;

-- Rule #11 + #22: Coverage audit - features below expected threshold
CREATE OR REPLACE VIEW v_coverage_audit AS
SELECT
    feature_name,
    owner_email,
    feature_type,
    expected_coverage,
    status
FROM feature_registry
WHERE status = 'ACTIVE'
ORDER BY expected_coverage ASC;

-- Glossary alignment view: shows feature types with glossary definitions
CREATE OR REPLACE VIEW v_feature_glossary AS
SELECT
    feature_name,
    feature_type,
    CASE feature_type
        WHEN 'numerical'   THEN 'Glossary: numerical data - represented as integers or real-valued numbers'
        WHEN 'categorical' THEN 'Glossary: categorical data - has a specific set of possible values'
        WHEN 'synthetic'   THEN 'Glossary: synthetic feature - assembled from one or more input features'
        WHEN 'embedding'   THEN 'Glossary: embedding - mapping to a lower-dimensional continuous vector space'
    END AS glossary_definition,
    normalization,
    value_range,
    expected_coverage,
    owner_email
FROM feature_registry
ORDER BY feature_type, feature_name;
