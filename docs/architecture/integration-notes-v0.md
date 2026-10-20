# Integration Notes v0

**Project:** Conversational Predictive Maintenance and Decision Support System  
**Status:** Contract alignment recorded for M0. OpenAPI, Health Summary schema, example and database schema agree with each other and are checked by contract tests in CI. This is not a claim that the described endpoints or modules are implemented.  
**Version:** 0.2

## 1. Purpose

This document records how the OpenAPI contract, the PostgreSQL schema and the Machine Health Summary fit together, so that implementation work does not mix identifiers, duplicate fields or imply unavailable model outputs.

Source-of-truth files:
- `docs/contracts/health-summary-v0.schema.json` and `docs/contracts/health-summary-v0.example.json`
- `docs/api/openapi.yaml`
- `docs/database/database-schema-v0.sql`
- `docker-compose.yml`

The contract tests in `tests/contracts/` verify that these files stay consistent. When one changes, update the others and this document in the same pull request.

## 2. Contract principles

1. **Readable public machine identifier:** the API field `machine_id` is the stable readable code, such as `FD001-E047`.
2. **Internal database identifier:** `machines.id` remains a UUID primary key and is never exposed as `machine_id`. Foreign keys use the UUID.
3. **Dataset identity:** `dataset_id` is one of `FD001`, `FD002`, `FD003` or `FD004`.
4. **Cycle is an index:** `cycle` is an observed C-MAPSS operating cycle, not a calendar timestamp.
5. **Application timestamps:** fields such as `generated_at` are application-generated UTC timestamps. C-MAPSS provides no real-world timestamps.
6. **Optional means omitted when unavailable:** do not return invented values, empty pseudo-results or `null` to represent an unimplemented capability.
7. **Prediction versus summary:** a prediction is a stored model result. A Health Summary is a composed response that may combine a prediction, risk result, explanation and recommendation.
8. **Research scope:** results are based on simulated C-MAPSS data and retrieved technical knowledge; they are not validated industrial maintenance instructions.

## 3. Identifier mapping

| Concept | Database | API | Status |
|---|---|---|---|
| Machine | `machines.id` UUID (internal), `machines.machine_code` unique | `machine_id` = `machine_code`, for example `FD001-E047`; used as the path parameter | Decided and in OpenAPI |
| Dataset / engine | `machines.dataset_id`, `machines.engine_id` | `dataset_id`; `engine_id` in machine responses | Decided |
| Prediction | `predictions.id` BIGSERIAL | `prediction_id`, integer (int64) | Decided; changed from a string example |
| Risk score | `risk_scores.id` BIGSERIAL | not exposed directly | Decided |
| Alert | `alerts.id` BIGSERIAL | `alert_id`, integer (int64) | Decided |
| Maintenance record | `maintenance_records.id` BIGSERIAL | `maintenance_id`, integer (int64) | Decided |
| User | `users.id` UUID | UUID in `created_by`, `assigned_to`, `acknowledged_by` | Decided |
| Chat session | `chat_sessions.id` UUID | `session_id` (UUID) | Decided |
| Model version | `model_versions.id` UUID (internal), `model_versions.version` | `model_version`, a readable string | Decided; composite display is still open (section 9) |

The API resolves the readable `machine_id` to `machines.id` in the repository or service layer. The two meanings never share a field name.

## 4. Health Summary field mapping

The Health Summary JSON Schema is the outward contract, and OpenAPI `HealthSummary` has the same fields.

| Health Summary field | Meaning | Database source / note |
|---|---|---|
| `machine_id` | Readable code | Serialize `machines.machine_code` |
| `dataset_id` | C-MAPSS subset | `machines.dataset_id` |
| `cycle` | Observed cycle index | Selected prediction cycle |
| `model_version` | Readable model version | Join `predictions.model_version_id` to `model_versions.version` |
| `rul.estimate` | Point RUL estimate in cycles | `predictions.predicted_rul` |
| `rul.interval.lower_bound` / `upper_bound` | Conformal interval | `predictions.lower_bound` / `upper_bound`; omit the interval when null |
| `rul.interval.coverage_level` | Nominal coverage, `0 < level < 1` | `predictions.coverage_level` (also constrained below 1 in the database); a nominal level, not a per-row guarantee |
| `rul.at_cap` | Estimate follows the capped-RUL convention | `predictions.at_cap` |
| `rul_threshold_probability.threshold_cycles` | RUL threshold N | `risk_scores.rul_threshold` |
| `rul_threshold_probability.probability` | Estimated P(RUL ≤ N) | `risk_scores.rul_threshold_probability`; an estimate, not a real-world failure probability |
| `risk_level` | `LOW`, `MEDIUM` or `HIGH` | `risk_scores.risk_level` |
| `thresholds_version` | Version of the risk-threshold configuration | `risk_scores.thresholds_version`; present if and only if `risk_level` is present |
| `trend` | Recent trend | No table; compute at request time, omit until validated |
| `top_contributors[].feature` | Exact model input feature name | `explanations.feature` |
| `top_contributors[].shap_value` | Signed SHAP value | `explanations.shap_value` |
| `top_contributors[].effect_on_rul` | Optional validated direction | Not stored; include only when the mapping is implemented and tested |
| `recommendation.summary` / `rule_id` | Rule-based investigation guidance | Derived from the versioned decision rule table; no table in schema v0 |
| `generated_at` | UTC time the summary was assembled | Application-generated |
| `disclaimer` | Fixed research-scope disclaimer | Constant, required in every summary |

`explanations.sensor` holds the base sensor of each feature. It supports sensor-level display and the sensor → component rules, and is exposed through `sensor_contributions` on the explanation endpoint.

## 5. Prediction record versus Health Summary

- **Prediction record** (`Prediction` in OpenAPI): `prediction_id`, `machine_id`, `cycle`, `predicted_rul`, optional `rul_interval`, `model_version`, `created_at`. It mirrors the `predictions` table.
- **Health Summary:** uses `rul.estimate` and top-level `risk_level`, with optional explanation and recommendation.
- **Mapping layer:** implement one explicit mapper from database prediction, risk, explanation and rule outputs to the Health Summary. Frontend code must not guess field correspondences.

## 6. Database integration notes

### Machines and sensor readings
- `machines.machine_code` is unique and is the external identifier. `(dataset_id, engine_id)` is also unique.
- `sensor_readings` stores operating settings and sensors in separate columns; the API returns a `sensors` object keyed by sensor name, so the serializer maps between them.
- `sensor_readings.created_at` is an ingestion timestamp, not an observation time. `(machine_id, cycle)` is unique and serves as the lookup index.

### Predictions and model versions
- `(machine_id, model_version_id, cycle)` is unique, so one prediction per machine, model and cycle. Revisit this if repeated inference runs need to be kept (section 9).
- At most one model version per dataset can be active, enforced by a partial unique index. `model_versions.calibration_version` records which conformal calibration belongs to a model.
- `coverage_level` is constrained to `0 < level < 1`, matching OpenAPI and the JSON Schema.

### Risk scores and explanations
- `risk_scores` is unique per `(prediction_id, rul_threshold, thresholds_version)`. If several thresholds are stored for one prediction, the Health Summary uses the row for the configured threshold N and the current thresholds version.
- `explanations` stores the ranked top SHAP contributors per prediction, with unique `(prediction_id, feature)` and `(prediction_id, contribution_rank)`. SHAP values describe model behaviour, not physical causation.

### Knowledge base
- `knowledge_documents` holds document metadata (unique on title and source). `knowledge_chunks` holds text chunks with `vector(384)` embeddings and an HNSW cosine index. The dimension must match the chosen embedding model; change it before the first ingestion if needed.
- The assistant's citations come from `knowledge_documents` and `knowledge_chunks`. A citation supports a retrieved claim; it does not prove a model prediction is correct.

### Disclaimer and provenance
- No table stores the disclaimer; it is a constant in the response.
- Record dataset, model version, preprocessing/feature version, cycle and generation time so results can be reproduced.

## 7. OpenAPI status

Done (checked by `tests/contracts/test_openapi_surface.py`):
- Health Summary and its sub-schemas match the JSON Schema.
- Readable machine path parameter; integer ids for predictions, alerts and maintenance records.
- JWT bearer security scheme, public `POST /auth/login` and `GET /health`, `401` on every protected operation, `403` on role-restricted operations.
- Endpoints from the scope: login, machines, sensor readings, predictions, health summary, explanation, risk and high-risk lists, maintenance (list, create, update), alerts (list, acknowledge/assign), chat and chat sessions.
- Role restrictions follow the permission matrix: maintenance create/update for Admin and Maintenance Engineer, alert update for Admin and Maintenance Manager.
- Enums for roles, dataset ids, alert status and severity, and maintenance status equal the database CHECK constraints.

Not yet in the contract:
- Admin functions: user management, risk thresholds, model version and knowledge base.
- Logs and monitoring endpoints, and the Viewer role (an Advanced item).
- Request examples for the new endpoints.

## 8. Runtime and deployment boundary

- `docker-compose.yml` defines one service, PostgreSQL 16 with pgvector (`pgvector/pgvector:pg16`), published on `127.0.0.1:5433` by default, with a named data volume and a TCP health check.
- On the first start with an empty volume the schema (`01-schema.sql`) and the development seed (`02-seed.sql`) load automatically. They do not run again for an existing volume; use `docker compose down -v` to rebuild.
- Credentials come from a local `.env` file that is not committed; `.env.example` holds placeholders.
- There is still no FastAPI, React, MLflow or LLM service in Compose. Add them in separate changes when their Dockerfiles exist. The model will run inside the backend process, not as a separate ML service.
- CI starts the Compose database and runs `scripts/check_db.sh` (13 tables, pgvector, seed counts, idempotent seed, one active model per dataset).

## 9. Contract tests and acceptance checklist

- [x] Readable `machine_id`; `dataset_id` limited to FD001–FD004.
- [x] `rul.estimate` required; interval ordered and containing the estimate (`semantic_errors`).
- [x] `coverage_level` strictly between 0 and 1.
- [x] `risk_level` is LOW, MEDIUM or HIGH in the schema, OpenAPI and database; `CRITICAL` is rejected.
- [x] `thresholds_version` present if and only if `risk_level` is present.
- [x] Example payload validates against the schema.
- [x] OpenAPI Health Summary has the same top-level fields as the JSON Schema.
- [x] OpenAPI references resolve; operation ids are unique; path parameters are declared.
- [x] Authentication and role rules are declared and match the permission matrix.
- [x] OpenAPI and database enums agree.
- [x] Database starts from a clean Compose run with schema, pgvector and an idempotent seed.
- [ ] Database-to-API mapping tests (readable machine code, model-version join) once the backend exists.
- [ ] Optional trend, recommendation, probability and interval fields are omitted, not fabricated, in real responses.
- [ ] `generated_at` is an application-generated UTC timestamp in real responses.

## 10. Decisions

Resolved:
1. **Public machine path:** the readable machine code.
2. **Required Health Summary fields:** `machine_id`, `dataset_id`, `cycle`, `model_version`, `rul` (with `estimate` and `at_cap`), `generated_at` and `disclaimer`. `risk_level`, `thresholds_version`, interval, probability, trend, contributors and recommendation are optional.
3. **Persistence of explanations:** top contributors are stored in `explanations`; trend and recommendation are computed at request time.
4. **Probability provenance:** v0 does not include a method field in the summary.

Still open (team to decide):
1. Model version display: `model_versions.version` only, or a composite with model name and dataset.
2. Repeated predictions: keep the current unique constraint or add a run identifier.
3. Who may call `POST /predictions` (the scope permission matrix does not list it; the contract currently allows all roles).
4. Embedding model and vector dimension.
5. Introducing migrations (for example Alembic) once the backend exists. Until then the SQL schema file is the single source of truth, and any change must also update this document and the tests.