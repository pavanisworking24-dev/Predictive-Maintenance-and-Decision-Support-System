-- ============================================================
-- Predictive Maintenance and Decision Support System
-- Database Schema v0
-- PostgreSQL 16
--
-- Project:
-- Conversational Predictive Maintenance and Decision Support System
--
-- Schema version: v0 (revision 1)
-- Core entities: 13
--
-- Revision 1 changes (no deployed database existed when these were made):
--   * pgvector extension and knowledge_chunks table (RAG embeddings)
--   * explanations table (stored SHAP contributors per prediction)
--   * at most one active model version per dataset
--   * unique constraints so the seed script is safe to re-run
--   * model_versions.calibration_version (links a model to its conformal
--     calibration), coverage_level restricted to 0 < level < 1
--   * removed a duplicate index on sensor_readings
-- Once the backend exists, further changes must go through migrations.
-- ============================================================


-- ============================================================
-- EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- pgvector: requires a PostgreSQL image that ships the extension
-- (docker-compose.yml uses pgvector/pgvector:pg16).
CREATE EXTENSION IF NOT EXISTS vector;


-- ============================================================
-- 1. USERS
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    role VARCHAR(30) NOT NULL
        CHECK (
            role IN (
                'ADMIN',
                'MAINTENANCE_MANAGER',
                'MAINTENANCE_ENGINEER'
            )
        ),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 2. MACHINES
-- ============================================================

CREATE TABLE machines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    machine_code VARCHAR(50) NOT NULL UNIQUE,

    dataset_id VARCHAR(10) NOT NULL
        CHECK (
            dataset_id IN (
                'FD001',
                'FD002',
                'FD003',
                'FD004'
            )
        ),

    engine_id INTEGER NOT NULL
        CHECK (engine_id > 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_machine_dataset_engine
        UNIQUE (dataset_id, engine_id)
);


-- ============================================================
-- 3. SENSOR READINGS
-- ============================================================

CREATE TABLE sensor_readings (
    id BIGSERIAL PRIMARY KEY,

    machine_id UUID NOT NULL
        REFERENCES machines(id)
        ON DELETE CASCADE,

    cycle INTEGER NOT NULL
        CHECK (cycle > 0),

    -- Operating settings
    op_setting_1 DOUBLE PRECISION,

    op_setting_2 DOUBLE PRECISION,

    op_setting_3 DOUBLE PRECISION,

    -- Sensor measurements
    sensor_1 DOUBLE PRECISION,

    sensor_2 DOUBLE PRECISION,

    sensor_3 DOUBLE PRECISION,

    sensor_4 DOUBLE PRECISION,

    sensor_5 DOUBLE PRECISION,

    sensor_6 DOUBLE PRECISION,

    sensor_7 DOUBLE PRECISION,

    sensor_8 DOUBLE PRECISION,

    sensor_9 DOUBLE PRECISION,

    sensor_10 DOUBLE PRECISION,

    sensor_11 DOUBLE PRECISION,

    sensor_12 DOUBLE PRECISION,

    sensor_13 DOUBLE PRECISION,

    sensor_14 DOUBLE PRECISION,

    sensor_15 DOUBLE PRECISION,

    sensor_16 DOUBLE PRECISION,

    sensor_17 DOUBLE PRECISION,

    sensor_18 DOUBLE PRECISION,

    sensor_19 DOUBLE PRECISION,

    sensor_20 DOUBLE PRECISION,

    sensor_21 DOUBLE PRECISION,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_sensor_reading_machine_cycle
        UNIQUE (machine_id, cycle)
);


-- ============================================================
-- 4. MODEL VERSIONS
-- ============================================================

CREATE TABLE model_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_name VARCHAR(100) NOT NULL,

    model_type VARCHAR(50) NOT NULL,

    dataset_id VARCHAR(10) NOT NULL
        CHECK (
            dataset_id IN (
                'FD001',
                'FD002',
                'FD003',
                'FD004'
            )
        ),

    version VARCHAR(50) NOT NULL,

    artifact_uri TEXT,

    feature_version VARCHAR(50),

    preprocessing_version VARCHAR(50),

    -- Version of the conformal calibration (calibration engines, bins,
    -- residuals) used together with this model
    calibration_version VARCHAR(50),

    is_active BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_model_version
        UNIQUE (model_name, version)
);


-- ============================================================
-- 5. PREDICTIONS
-- ============================================================

CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,

    machine_id UUID NOT NULL
        REFERENCES machines(id)
        ON DELETE CASCADE,

    model_version_id UUID NOT NULL
        REFERENCES model_versions(id),

    cycle INTEGER NOT NULL
        CHECK (cycle > 0),

    predicted_rul DOUBLE PRECISION NOT NULL
        CHECK (predicted_rul >= 0),

    lower_bound DOUBLE PRECISION,

    upper_bound DOUBLE PRECISION,

    coverage_level DOUBLE PRECISION,

    at_cap BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_prediction_machine_model_cycle
        UNIQUE (
            machine_id,
            model_version_id,
            cycle
        ),

    CONSTRAINT chk_prediction_interval
        CHECK (
            lower_bound IS NULL
            OR upper_bound IS NULL
            OR (
                lower_bound >= 0
                AND upper_bound >= lower_bound
            )
        ),

    CONSTRAINT chk_coverage_level
        CHECK (
            coverage_level IS NULL
            OR (
                coverage_level > 0
                AND coverage_level < 1
            )
        )
);


-- ============================================================
-- 6. RISK SCORES
-- ============================================================

CREATE TABLE risk_scores (
    id BIGSERIAL PRIMARY KEY,

    machine_id UUID NOT NULL
        REFERENCES machines(id)
        ON DELETE CASCADE,

    prediction_id BIGINT NOT NULL
        REFERENCES predictions(id)
        ON DELETE CASCADE,

    risk_level VARCHAR(20) NOT NULL
        CHECK (
            risk_level IN (
                'LOW',
                'MEDIUM',
                'HIGH'
            )
        ),

    -- Configured RUL threshold N
    rul_threshold INTEGER NOT NULL
        CHECK (rul_threshold >= 0),

    -- Estimated probability that RUL <= threshold
    rul_threshold_probability DOUBLE PRECISION
        CHECK (
            rul_threshold_probability IS NULL
            OR (
                rul_threshold_probability >= 0
                AND rul_threshold_probability <= 1
            )
        ),

    thresholds_version VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- One risk row per prediction, threshold and thresholds version.
    -- NULLS NOT DISTINCT (PostgreSQL 15+) also covers a missing version.
    CONSTRAINT uq_risk_score_prediction_threshold
        UNIQUE NULLS NOT DISTINCT (
            prediction_id,
            rul_threshold,
            thresholds_version
        )
);


-- ============================================================
-- 7. ALERTS
-- ============================================================

CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,

    machine_id UUID NOT NULL
        REFERENCES machines(id)
        ON DELETE CASCADE,

    prediction_id BIGINT
        REFERENCES predictions(id)
        ON DELETE SET NULL,

    assigned_to UUID
        REFERENCES users(id)
        ON DELETE SET NULL,

    acknowledged_by UUID
        REFERENCES users(id)
        ON DELETE SET NULL,

    alert_type VARCHAR(50) NOT NULL,

    severity VARCHAR(20) NOT NULL
        CHECK (
            severity IN (
                'LOW',
                'MEDIUM',
                'HIGH'
            )
        ),

    message TEXT NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN'
        CHECK (
            status IN (
                'OPEN',
                'ACKNOWLEDGED',
                'RESOLVED'
            )
        ),

    acknowledged_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_alert_acknowledgement
        CHECK (
            (
                status = 'OPEN'
                AND acknowledged_at IS NULL
            )
            OR status IN (
                'ACKNOWLEDGED',
                'RESOLVED'
            )
        )
);


-- ============================================================
-- 8. MAINTENANCE RECORDS
-- ============================================================

CREATE TABLE maintenance_records (
    id BIGSERIAL PRIMARY KEY,

    machine_id UUID NOT NULL
        REFERENCES machines(id)
        ON DELETE CASCADE,

    created_by UUID NOT NULL
        REFERENCES users(id),

    title VARCHAR(200) NOT NULL,

    description TEXT,

    action TEXT,

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN'
        CHECK (
            status IN (
                'OPEN',
                'IN_PROGRESS',
                'COMPLETED',
                'CANCELLED'
            )
        ),

    scheduled_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_maintenance_dates
        CHECK (
            completed_at IS NULL
            OR scheduled_at IS NULL
            OR completed_at >= scheduled_at
        )
);


-- ============================================================
-- 9. CHAT SESSIONS
-- ============================================================

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    machine_id UUID
        REFERENCES machines(id)
        ON DELETE SET NULL,

    title VARCHAR(200),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 10. CHAT MESSAGES
-- ============================================================

CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,

    session_id UUID NOT NULL
        REFERENCES chat_sessions(id)
        ON DELETE CASCADE,

    role VARCHAR(20) NOT NULL
        CHECK (
            role IN (
                'USER',
                'ASSISTANT'
            )
        ),

    content TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 11. KNOWLEDGE DOCUMENTS
-- ============================================================

CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    title VARCHAR(300) NOT NULL,

    source VARCHAR(200) NOT NULL,

    source_url TEXT,

    document_type VARCHAR(100),

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_knowledge_document_title_source
        UNIQUE (title, source)
);


-- ============================================================
-- 12. EXPLANATIONS (stored SHAP contributors)
-- ============================================================

CREATE TABLE explanations (
    id BIGSERIAL PRIMARY KEY,

    prediction_id BIGINT NOT NULL
        REFERENCES predictions(id)
        ON DELETE CASCADE,

    -- 1 = largest absolute contribution for this prediction
    contribution_rank INTEGER NOT NULL
        CHECK (contribution_rank > 0),

    -- Exact model input feature name, for example sensor_11_rolling_mean_5
    feature VARCHAR(100) NOT NULL,

    -- Base sensor the feature belongs to (sensor-level aggregation), if any
    sensor VARCHAR(20),

    shap_value DOUBLE PRECISION NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_explanation_prediction_feature
        UNIQUE (prediction_id, feature),

    CONSTRAINT uq_explanation_prediction_rank
        UNIQUE (prediction_id, contribution_rank)
);


-- ============================================================
-- 13. KNOWLEDGE CHUNKS (RAG text chunks and embeddings)
-- ============================================================

CREATE TABLE knowledge_chunks (
    id BIGSERIAL PRIMARY KEY,

    document_id UUID NOT NULL
        REFERENCES knowledge_documents(id)
        ON DELETE CASCADE,

    chunk_index INTEGER NOT NULL
        CHECK (chunk_index >= 0),

    content TEXT NOT NULL,

    -- Page, section, sensor tags and other retrieval metadata
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Embedding dimension must match the chosen embedding model.
    -- 384 fits common small sentence-embedding models; change it before
    -- the first ingestion if the team picks a different model.
    embedding vector(384),

    embedding_model VARCHAR(100),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_knowledge_chunk_document_index
        UNIQUE (document_id, chunk_index)
);


-- ============================================================
-- INDEXES
-- ============================================================


-- Sensor readings
-- (machine_id, cycle) is already indexed by uq_sensor_reading_machine_cycle.


-- Model versions: at most one active model per dataset
CREATE UNIQUE INDEX uq_model_versions_one_active_per_dataset
    ON model_versions(dataset_id)
    WHERE is_active;


-- Predictions
CREATE INDEX idx_predictions_machine_cycle
    ON predictions(machine_id, cycle);

CREATE INDEX idx_predictions_model
    ON predictions(model_version_id);


-- Risk scores
CREATE INDEX idx_risk_scores_machine
    ON risk_scores(machine_id);

CREATE INDEX idx_risk_scores_level
    ON risk_scores(risk_level);


-- Alerts
CREATE INDEX idx_alerts_status
    ON alerts(status);

CREATE INDEX idx_alerts_machine
    ON alerts(machine_id);

CREATE INDEX idx_alerts_prediction
    ON alerts(prediction_id);


-- Maintenance
CREATE INDEX idx_maintenance_machine
    ON maintenance_records(machine_id);


-- Chat
CREATE INDEX idx_chat_sessions_machine
    ON chat_sessions(machine_id);

CREATE INDEX idx_chat_messages_session
    ON chat_messages(session_id);


-- Knowledge documents
CREATE INDEX idx_knowledge_documents_type
    ON knowledge_documents(document_type);


-- Knowledge chunks: approximate nearest-neighbour search (cosine distance)
CREATE INDEX idx_knowledge_chunks_embedding
    ON knowledge_chunks
    USING hnsw (embedding vector_cosine_ops);


-- ============================================================
-- END OF DATABASE SCHEMA v0
-- ============================================================