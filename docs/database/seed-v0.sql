
-- ============================================================
-- Predictive Maintenance and Decision Support System
-- M0 Seed Data v0
-- Purpose: Validate database relationships with sample data
-- ============================================================

BEGIN;

-- 1. Create a demo user
INSERT INTO users (
    name,
    email,
    password_hash,
    role
)
VALUES (
    'Demo Administrator',
    'admin.demo@example.com',
    'NOT_FOR_AUTHENTICATION',
    'ADMIN'
)
ON CONFLICT (email) DO NOTHING;


-- 2. Register one sample FD001 engine
INSERT INTO machines (
    machine_code,
    dataset_id,
    engine_id
)
VALUES (
    'FD001-E001',
    'FD001',
    1
)
ON CONFLICT (machine_code) DO NOTHING;


-- 3. Register a sample XGBoost model
INSERT INTO model_versions (
    model_name,
    model_type,
    dataset_id,
    version,
    artifact_uri,
    feature_version,
    preprocessing_version,
    is_active
)
VALUES (
    'XGBoost RUL Baseline',
    'XGBoost',
    'FD001',
    'v0.1-demo',
    'local://demo-model',
    'features-v0',
    'preprocessing-v0',
    TRUE
)
ON CONFLICT (model_name, version) DO NOTHING;


-- 4. Insert three illustrative sensor readings
INSERT INTO sensor_readings (
    machine_id,
    cycle,
    op_setting_1,
    op_setting_2,
    op_setting_3,
    sensor_2,
    sensor_3,
    sensor_4,
    sensor_7,
    sensor_11,
    sensor_12
)
SELECT
    m.id,
    sample.cycle,
    sample.op1,
    sample.op2,
    sample.op3,
    sample.s2,
    sample.s3,
    sample.s4,
    sample.s7,
    sample.s11,
    sample.s12
FROM machines AS m
CROSS JOIN (
    VALUES
        (1, 0.0023::double precision, 0.0002::double precision, 100.0::double precision,
         642.0::double precision, 1589.0::double precision, 1400.0::double precision,
         554.0::double precision, 47.0::double precision, 521.0::double precision),
        (2, 0.0021::double precision, 0.0003::double precision, 100.0::double precision,
         643.0::double precision, 1590.0::double precision, 1402.0::double precision,
         553.0::double precision, 48.0::double precision, 522.0::double precision),
        (3, 0.0020::double precision, 0.0002::double precision, 100.0::double precision,
         644.0::double precision, 1592.0::double precision, 1404.0::double precision,
         552.0::double precision, 49.0::double precision, 523.0::double precision)
) AS sample(
    cycle, op1, op2, op3, s2, s3, s4, s7, s11, s12
)
WHERE m.machine_code = 'FD001-E001'
ON CONFLICT (machine_id, cycle) DO NOTHING;


-- 5. Insert three illustrative RUL predictions
INSERT INTO predictions (
    machine_id,
    model_version_id,
    cycle,
    predicted_rul,
    lower_bound,
    upper_bound,
    coverage_level,
    at_cap
)
SELECT
    m.id,
    mv.id,
    sample.cycle,
    sample.predicted_rul,
    sample.lower_bound,
    sample.upper_bound,
    0.90,
    FALSE
FROM machines AS m
CROSS JOIN model_versions AS mv
CROSS JOIN (
    VALUES
        (1, 120.0::double precision, 110.0::double precision, 130.0::double precision),
        (2, 115.0::double precision, 105.0::double precision, 125.0::double precision),
        (3, 108.0::double precision, 98.0::double precision, 118.0::double precision)
) AS sample(cycle, predicted_rul, lower_bound, upper_bound)
WHERE m.machine_code = 'FD001-E001'
  AND mv.model_name = 'XGBoost RUL Baseline'
  AND mv.version = 'v0.1-demo'
ON CONFLICT (machine_id, model_version_id, cycle) DO NOTHING;


-- 6. Insert illustrative risk scores
INSERT INTO risk_scores (
    machine_id,
    prediction_id,
    risk_level,
    rul_threshold,
    rul_threshold_probability,
    thresholds_version
)
SELECT
    p.machine_id,
    p.id,
    sample.risk_level,
    30,
    sample.estimated_probability,
    'risk-rules-v0'
FROM predictions AS p
JOIN machines AS m
    ON m.id = p.machine_id
JOIN model_versions AS mv
    ON mv.id = p.model_version_id
JOIN (
    VALUES
        (1, 'LOW'::varchar, 0.05::double precision),
        (2, 'LOW'::varchar, 0.08::double precision),
        (3, 'LOW'::varchar, 0.12::double precision)
) AS sample(cycle, risk_level, estimated_probability)
    ON sample.cycle = p.cycle
WHERE m.machine_code = 'FD001-E001'
  AND mv.model_name = 'XGBoost RUL Baseline'
  AND mv.version = 'v0.1-demo'
ON CONFLICT DO NOTHING;


-- 7. Register a sample knowledge document
INSERT INTO knowledge_documents (
    title,
    source,
    source_url,
    document_type,
    description
)
VALUES (
    'Predictive Maintenance Demo Reference',
    'Project Demo Seed',
    NULL,
    'DEMO',
    'Placeholder document record for validating the knowledge-document schema.'
)
ON CONFLICT DO NOTHING;


COMMIT;