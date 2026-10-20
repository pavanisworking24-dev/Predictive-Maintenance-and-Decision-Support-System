# System Architecture v0

**Project:** Conversational Predictive Maintenance and Decision Support System  
**Status:** M0 architecture baseline — contracts aligned (see `integration-notes-v0.md`); components are staged and not all implemented  
**Version:** 0.2.0  
**Scope:** Historical, batch-oriented NASA C-MAPSS research case study

## 1. Purpose

This document defines the proposed logical architecture, component responsibilities, data flow, and integration boundaries for the first end-to-end version of the project. It is an architecture baseline, not evidence that every component has been implemented.

The system is research-oriented decision support. It estimates Remaining Useful Life (RUL), presents model-derived risk and uncertainty information, explains model behavior, and retrieves technical references to help users investigate a result.

## 2. Scope and explicit limitations

### Included in the planned system

- Historical C-MAPSS data processing, beginning with FD001 and extending to FD001–FD004 through a shared data interface.
- Engine-level train, validation, calibration, and test separation.
- RUL prediction, conformal prediction intervals, configurable RUL-threshold risk estimates, and risk bands.
- SHAP explanations of model behavior.
- A React dashboard and FastAPI application API.
- PostgreSQL persistence. pgvector is enabled in the local database and the schema has a `knowledge_chunks` table for embeddings; ingestion and retrieval are not yet implemented.
- Retrieval-augmented conversational assistance using a provider-independent LLM wrapper.
- Local containerized development and automated checks through GitHub Actions.
- Reproducible model experiments and a manual model registry using MLflow in a later milestone.

### Excluded from the current scope

- Live industrial telemetry, streaming ingestion, and real-time sensor monitoring.
- Autonomous control of equipment or automatic execution of maintenance procedures.
- Claims that results on simulated turbofan data establish performance on real industrial machines.
- Treating a model explanation as proof of a physical failure mechanism.
- Treating a model-derived RUL-threshold probability as a guaranteed real-world failure probability.

**Required disclaimer:** “Research-oriented decision support based on simulated C-MAPSS data and retrieved technical knowledge.”

## 3. High-level architecture

The initial application uses a modular monolith: one FastAPI backend owns API routing, business rules, model inference, explanation orchestration, retrieval, and LLM coordination. The predictive model is loaded and called inside the backend process; a separate ML microservice is not part of the current plan.

~~~mermaid
flowchart TD
    D[Historical NASA C-MAPSS files] --> P[Data validation and preprocessing]
    P --> F[Feature engineering]
    F --> T[Training and evaluation pipeline]
    T --> M[Versioned model and preprocessing artifacts]
    M --> B[FastAPI application backend]
    P --> DB[(PostgreSQL)]
    B --> DB
    B --> R[Risk and conformal uncertainty logic]
    B --> X[SHAP explanation logic]
    B --> K[Knowledge retrieval]
    K --> V[(PostgreSQL / pgvector)]
    K --> L[Provider-independent LLM wrapper]
    R --> H[Machine Health Summary]
    X --> H
    H --> B
    B --> UI[React dashboard and chat UI]
    UI --> B
    CI[GitHub Actions] --> Q[Automated contract and test checks]
~~~

The diagram represents intended component boundaries. It does not imply that all arrows or services are already implemented. In particular, the retrieval pipeline (the database side, pgvector, is ready) and MLflow integration are staged capabilities.

## 4. Component responsibilities

| Component | Responsibilities | Important boundary |
|---|---|---|
| Dataset pipeline | Load a selected C-MAPSS subset, validate columns and engine/cycle structure, derive RUL labels, create causal features, and preserve engine-level splits | No row-level random split across cycles of the same engine |
| Model training and evaluation | Train baseline models and the selected XGBoost model; reproduce metrics and artifacts | Official test evaluation uses each test engine's final observed cycle and corresponding supplied RUL target |
| Model artifact interface | Package model, feature order, preprocessing configuration, subset identity, and versions | Backend must reject incompatible feature or subset inputs rather than silently reorder or guess |
| FastAPI backend | Expose REST endpoints; validate requests; orchestrate inference, uncertainty, risk, explanations, health summaries, and assistant calls | No separate inference microservice in v0 |
| PostgreSQL | Persist machine registry, historical sensor readings, model versions, predictions, risk results, alerts, maintenance records, and chat records as supported by the database contract | Internal primary keys are distinct from readable public machine codes |
| Conformal uncertainty module | Produce intervals from a held-out calibration set and report nominal coverage level | Calibration data must not be reused as training data or test data; coverage is empirical, not an individual-prediction guarantee |
| Risk module | Assign configured risk bands and, when implemented and evaluated, estimate P(RUL ≤ threshold cycles) | Probability is an estimate, not ground-truth failure probability |
| SHAP module | Produce local/global feature attributions for supported model versions | SHAP describes model behavior; it does not independently establish physical causation |
| Knowledge retrieval | Retrieve relevant, traceable passages from curated technical sources and sensor/component/degradation reference material | Retrieval evidence supports the assistant's explanation, not the numerical validity of a prediction |
| LLM wrapper | Invoke the selected provider with retrieved context and structured machine-health context; log provider/model and evaluation metadata | Do not invent values, citations, maintenance history, or unsupported causal claims |
| React frontend | Show fleet/machine summaries, prediction details, explanations, alerts, and conversational responses | Render only fields returned by the API; optional unavailable fields should be omitted or shown as unavailable, never fabricated |
| GitHub Actions | Run available automated checks, including contract/schema tests as they are added | A passing placeholder workflow is not evidence of model quality |
| MLflow (later milestone) | Track experiments and artifacts; support a manual model registry | Not required to be running in the first M0 vertical slice |

## 5. Data flow

1. Select a C-MAPSS subset explicitly (FD001, FD002, FD003, or FD004).
2. Load training data, test data, and the official test RUL file through the same dataset interface.
3. Validate schema, expected sensor/settings columns, engine identifiers, cycle ordering, missing values, and duplicate engine-cycle rows.
4. Construct labels and causal features. Apply the agreed RUL training-label cap (125 cycles) consistently where applicable, while preserving the distinction between a capped target and an exact physical RUL.
5. Split by engine identity, not by individual rows. Keep training, validation, calibration, and final test engines separate.
6. Train and evaluate model candidates. Store the subset, feature/preprocessing versions, metrics, and model artifact reference.
7. At inference, load the compatible model artifact and process the selected machine at a specified observed cycle.
8. Generate an RUL estimate. Add a conformal interval only when a compatible calibrated interval is available. Add a threshold probability only when its method is implemented and evaluated.
9. Calculate the configured risk band. Generate SHAP contributors only when explanation output is available.
10. Build the Machine Health Summary from actual outputs and available provenance.
11. For a user question, retrieve relevant technical passages and provide them to the LLM with the structured summary. Validate that numerical claims in the response agree with the summary.
12. Return the API response to the frontend and persist applicable prediction, risk, explanation, and conversation records.

### Evaluation protocol

- **Primary test protocol:** one prediction for the final observed cycle of each test engine, evaluated against the corresponding value in the official test RUL file.
- **Primary metrics:** MAE, RMSE, R², and the NASA/PHM08 asymmetric score.
- **Secondary analysis:** all-cycle or trajectory-level evaluation, clearly labelled as secondary.
- **Cross-subset experiment:** keep within-subset evaluation distinct from the experiment that trains on FD001 and evaluates on another subset. Do not concatenate all four training files and describe that as the same experiment.
- **Uncertainty:** report empirical interval coverage and interval width overall, by RUL range, and by subset where sample size permits.
- **Risk probability:** evaluate calibration with appropriate reliability analysis and Brier score. State limitations, especially where official test engines have a different RUL distribution from calibration engines.

## 6. Identity, cycle, and timestamp conventions

### Machine identity

- Database primary key: internal UUID named id in the machine registry.
- Public-facing machine_id: readable identifier such as FD001-E047.
- Dataset engine identity is represented by the pair dataset_id and engine_id.
- The database should enforce uniqueness for the dataset/engine pair and for the readable identifier.
- API paths and response schemas must explicitly state whether they accept the internal UUID or public-facing code. They must not use the same field name for both meanings.

Decided and implemented in docs/api/openapi.yaml: public routes and responses use the readable code as `machine_id` (for example `/machines/FD001-E047/health-summary`). The service layer resolves it to the internal UUID. Prediction, alert and maintenance ids are integers matching the database BIGSERIAL keys.

### Cycle and timestamps

- cycle is the observed operating-cycle index from C-MAPSS.
- It is not a wall-clock timestamp.
- C-MAPSS does not provide a real-world observation timestamp for each cycle. Any application timestamp must be labelled as application-generated metadata.
- generated_at is generated by the application in UTC and should be serialized as an ISO 8601 timestamp with a UTC offset, preferably Z.

## 7. Machine Health Summary contract direction

The Health Summary is the canonical, structured handoff between prediction logic, the dashboard, and conversational assistance. Its exact JSON Schema and example belong in the contract files and must be kept consistent with OpenAPI and database mappings.

The agreed field direction is:

- machine_id: readable public identifier, for example FD001-E047.
- dataset_id: one of FD001–FD004.
- cycle: observed cycle index.
- model_version: version of the model used.
- rul.estimate: non-negative RUL estimate in cycles.
- rul.at_cap: indicates whether the displayed/target convention is affected by the RUL cap.
- rul.interval: optional object with lower_bound, upper_bound, and nominal coverage_level.
- rul_threshold_probability: optional object with threshold_cycles and probability, only when the estimation method is implemented and evaluated.
- risk_level: LOW, MEDIUM, or HIGH, when the core risk classifier is part of the response.
- thresholds_version: version of the risk-threshold configuration; present if and only if risk_level is present.
- trend: optional, only when computed.
- top_contributors: optional list of actual explanation outputs using feature and shap_value; effect_on_rul is included only if its sign-to-effect mapping is implemented and validated.
- recommendation: optional object containing a rule-grounded summary and optional rule_id.
- generated_at: application-generated UTC timestamp.
- disclaimer: the research disclaimer above.

Do not fabricate optional fields, default missing intervals to zero-width intervals, invent SHAP contributors, or manufacture timestamps from cycles. A conformal coverage_level is a nominal target level and must not be described as a guarantee for an individual prediction.

The OpenAPI file, the JSON Schema and the example now agree on these field names, and contract tests in CI keep them aligned. The separate Prediction resource keeps `predicted_rul`, mirroring the `predictions` table; a mapping layer composes the Health Summary from stored prediction, risk, explanation and rule outputs. This describes the contract; the backend that serves it is not yet implemented.

## 8. Knowledge and conversational response boundaries

The knowledge base should connect sensor or engineered-feature terminology to candidate components and documented degradation mechanisms using traceable sources. Such mappings are hypotheses or documented associations, not proof that a particular component has failed.

The assistant should receive:
- The structured Health Summary and its available model/data provenance.
- Retrieved technical passages with source identifiers and passage references.
- A clear instruction to distinguish prediction output from retrieved background knowledge.

The assistant must not:
- Change or contradict numerical RUL/risk values without an explicit new calculation.
- Present retrieved material as the evidence that the ML prediction is correct.
- Claim that SHAP establishes a physical cause.
- Recommend an unsupported maintenance procedure as authoritative.
- Answer beyond the retrieved context while implying that a source supports it.

Evaluation should include normal questions, insufficient-context questions, out-of-scope/adversarial prompts, citation checks, and automated numerical consistency checks against the source summary. Target an initial curated set of approximately 30–50 evaluation questions; record the actual set and results.

## 9. Deployment and local development

### M0 baseline

- Docker Compose starts PostgreSQL with pgvector. The schema and a development seed load automatically on the first start; the FastAPI backend will be added when its container exists.
- PostgreSQL persists data through a named volume.
- Environment-specific credentials and provider keys are supplied through environment configuration (a local `.env` file, not committed; `.env.example` holds placeholders).
- GitHub Actions validates the contract files, runs the contract tests and ruff, and starts the Compose database to check the schema, pgvector, the seed and key constraints (`scripts/check_db.sh`).
- Mock responses may be used to unblock frontend integration, but must be clearly identified as mock data.

### Later additions

- React frontend container and full application wiring.
- Document ingestion, embedding and retrieval over the pgvector-enabled database (the embedding dimension in `knowledge_chunks` must match the chosen model).
- MLflow tracking and manual registry.
- Model artifacts packaged or mounted in a controlled way so the backend loads the intended model version and compatible preprocessing/features.

The checked-in docker-compose.yml currently defines PostgreSQL (with pgvector) only. It should not be described as an already-working full-stack deployment. Credentials come from the local `.env` file; development values must not be reused as production credentials.

## 10. Security, reliability, and observability

- Validate request bodies, query parameters, dataset identifiers, cycle ranges, and model-version compatibility.
- Keep secrets out of Git and avoid logging credentials or sensitive user content.
- Use structured application logs with request identifiers and model-version context.
- Provide backend health/readiness checks as implementation proceeds.
- Return consistent API errors and avoid leaking stack traces to clients.
- Record prediction provenance sufficient to reproduce or audit the output: dataset/subset, model version, preprocessing/feature version, cycle, and generation timestamp where available.
- Ensure a prediction failure or unavailable explanation does not lead to fabricated Health Summary fields.
- Log LLM provider/model version and relevant evaluation metadata; log prompts/responses according to an agreed privacy policy.
- Keep risk thresholds configurable and versioned.

## 11. Key integration contracts

| Contract | Owner / source of truth | Consumers | M0 rule |
|---|---|---|---|
| OpenAPI | docs/api/openapi.yaml | Backend, frontend, contract tests | One canonical definition per API field; validate references and schemas |
| Health Summary JSON Schema | docs/contracts/health-summary-v0.schema.json | Backend, frontend, LLM numerical checker | Keep names and required/optional policy aligned with OpenAPI |
| Health Summary example | docs/contracts/health-summary-v0.example.json | Tests, frontend mock integration | Validate against the schema; mark values illustrative |
| Database schema | docs/database/database-schema-v0.sql | Backend persistence | Document UUID-to-readable-ID mapping and JSON/API field mappings |
| Feature/model artifact metadata | ML pipeline and model package | FastAPI inference | Reject incompatible subset, feature order, or preprocessing version |
| Knowledge-source inventory | docs/Knowledge/knowledge-source-inventory-v0.md | Retrieval pipeline and assistant | Each source must have a stable reference and provenance |
| CI workflow | .github/workflows/ci.yml | Contributors and reviewers | A failed contract/test check blocks acceptance of the affected change |

Field-by-field mappings between the database, OpenAPI and the Health Summary are in docs/architecture/integration-notes-v0.md.

## 12. Contract alignment status

Done:

1. Public readable `machine_id` versus internal UUID is settled (section 6).
2. Health Summary names are aligned: `rul.estimate`, top-level `risk_level` with `thresholds_version`, `shap_value`, `recommendation`.
3. Required and optional fields are defined in the JSON Schema; optional fields are omitted when unavailable.
4. The research disclaimer is a required field of the Health Summary schema.
5. The Prediction resource and the Health Summary are separate, with a documented mapping (integration notes).
6. Database and API semantics are aligned: `coverage_level` is strictly between 0 and 1, `risk_level` allows LOW, MEDIUM and HIGH everywhere, explanations have a table.
7. CI validates the OpenAPI document, the JSON Schema and the example payload, runs the contract tests, and starts the Compose database.
8. pgvector is enabled in the Compose database and the schema has `knowledge_chunks`. Retrieval itself is not yet operational and must not be described as such.

Still open:

1. Add the backend service and its health check to Compose when the backend exists; keep Compose described as the database environment until then.
2. Decisions listed in section 10 of the integration notes (model version display, repeated predictions, who may call POST /predictions, embedding model and dimension).
3. Move to migrations (for example Alembic) once the backend exists.

## 13. Architecture acceptance criteria for M0

- [ ] All five team members can explain the major components and their boundaries.
- [ ] Historical-only scope and the research disclaimer are explicit.
- [ ] The diagram and text agree that inference runs inside FastAPI.
- [x] Machine UUID, readable machine identifier, dataset ID, engine ID, cycle, and timestamps have distinct meanings.
- [x] OpenAPI, Health Summary schema/example, and database mappings have a documented field-by-field alignment (integration notes).
- [ ] Optional outputs are omitted when unavailable; no synthetic explanations or timestamps are generated.
- [ ] Mock data is labelled and validates against the intended contract.
- [x] CI checks the contract and schema.
- [ ] Every item described as implemented is backed by code or a passing test; planned items remain labelled as planned.

## 14. Decision log

| Decision | Current baseline |
|---|---|
| Application shape | Modular monolith |
| Backend | FastAPI |
| Model inference | Inside FastAPI; no separate ML microservice |
| Frontend | React |
| Database | PostgreSQL 16 with pgvector enabled in the local Compose database; schema includes explanations and knowledge chunks |
| Initial data | Historical NASA C-MAPSS data |
| Dataset strategy | Shared loader/interface; evaluate each subset separately before cross-subset experiments |
| Uncertainty | Split conformal prediction intervals |
| Explanation | SHAP, interpreted as model attribution rather than causation |
| Risk | Configurable risk bands; probability estimate only after evaluation |
| Conversational assistant | RAG with a provider-independent LLM wrapper and numerical consistency checks |
| Experiment tracking | MLflow planned for a later milestone |
| Live telemetry | Explicitly out of scope for current version |
| Health Summary identity | Readable public machine_id; internal database UUID remains separate |
| Authentication and roles | JWT bearer tokens; roles Admin, Maintenance Manager and Maintenance Engineer, with role-restricted operations declared in OpenAPI |
| Missing optional outputs | Omit them rather than fabricate values |

---

**Document status:** M0 architecture baseline with aligned contracts. Update the architecture and linked contracts together when a decision changes; do not let the diagram, OpenAPI, schema, database, and implementation drift independently.