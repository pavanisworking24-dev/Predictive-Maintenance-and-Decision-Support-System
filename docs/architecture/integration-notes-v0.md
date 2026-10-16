# Integration Notes v0

**Project:** Conversational Predictive Maintenance and Decision Support System  
**Status:** Contract alignment proposal for M0; not a claim that the described endpoints or modules are implemented.  
**Branch:** `docs/m0-architecture-v0`

## 1. Purpose

This document records how the existing OpenAPI draft, PostgreSQL schema, and agreed Machine Health Summary should fit together. It distinguishes current repository definitions from the proposed v0 contract so that implementation work does not silently mix identifiers, duplicate fields, or imply unavailable model outputs.

Reviewed repository files:
- `docs/api/openapi.yaml`
- `docs/database/database-schema-v0.sql`
- `docker-compose.yml`
- `README.md`

The architecture and contract are still drafts. Treat the decisions below as proposed v0 alignment until the team accepts and implements them.

## 2. Contract principles

1. **Readable public machine identifier:** API response field `machine_id` is the stable readable code, such as `FD001-E047`.
2. **Internal database identifier:** `machines.id` remains a UUID primary key and is not the public Health Summary `machine_id`. Foreign keys continue to use the UUID.
3. **Dataset identity:** `dataset_id` is one of `FD001`, `FD002`, `FD003`, or `FD004`.
4. **Cycle is an index:** `cycle` identifies an observed C-MAPSS operating cycle, not a calendar timestamp.
5. **Application timestamps:** API fields such as `generated_at` are application-generated timestamps in UTC. C-MAPSS cycle rows do not provide real-world timestamps.
6. **Optional means omitted when unavailable:** Do not return made-up values, empty pseudo-results, or `null` solely to represent an unimplemented capability. The schema should define the agreed behavior consistently.
7. **Prediction versus summary:** A prediction record is a stored model result. A Health Summary is a composed response that may combine a prediction, risk result, explanation, and recommendation.
8. **Research scope:** Results are based on simulated C-MAPSS data and retrieved technical knowledge; they are not validated industrial maintenance instructions.

## 3. Identifier mapping

| Concept | Current repository definition | Proposed API convention |
|---|---|---|
| Machine database primary key | `machines.id UUID` | Internal only; used in foreign keys |
| Readable machine code | `machines.machine_code`, unique; example `FD001-E047` | Expose as `machine_id` in the agreed Health Summary and as a clearly named readable code in machine inventory responses |
| OpenAPI machine path parameter | `machine_id` is currently documented as UUID | Change path parameter to a readable machine code, or explicitly rename it `machine_uuid` if the team chooses internal UUID paths. Do not use one name for both meanings |
| Dataset | `machines.dataset_id` | `dataset_id`, enum FD001–FD004 |
| Dataset engine index | `machines.engine_id` | Internal/source identifier; not a substitute for readable `machine_id` |
| Prediction primary key | `predictions.id BIGSERIAL` | API may expose as `prediction_id`; conversion/serialization must be explicit |
| Model version primary key | `model_versions.id UUID` | Internal foreign key; API-facing `model_version` is a readable version string unless an endpoint explicitly requests a UUID |

### Important path decision

The existing OpenAPI defines `/machines/{machine_id}` with a UUID parameter, while the agreed Health Summary uses a readable `machine_id`. Before implementing endpoints, choose one consistent route convention. Recommended v0: use the readable code in public routes (for example, `/machines/FD001-E047/health-summary`) and resolve it to `machines.id` inside the repository/service layer. If changing all existing paths now is too disruptive, rename the current parameter to `machine_uuid` and document the distinction. Do not ship an ambiguous mixed convention.

## 4. Health Summary field mapping

The agreed Health Summary shape is the outward contract. The current OpenAPI `HealthSummary` schema differs in several places.

| Health Summary field | Agreed meaning | Current OpenAPI | Database source / integration note |
|---|---|---|---|
| `machine_id` | Readable code, e.g. `FD001-E047` | UUID | Resolve `machines.id` internally; serialize `machines.machine_code` |
| `dataset_id` | C-MAPSS subset | Present | `machines.dataset_id` |
| `cycle` | Observed cycle index | Present | Selected cycle from `sensor_readings.cycle` / prediction |
| `model_version` | Readable model version | Present | Join `predictions.model_version_id` to `model_versions.id`; serialize `model_versions.version` or a documented composite version |
| `rul.estimate` | Point RUL estimate in cycles | Current field is `rul.point` | `predictions.predicted_rul`; rename response field to `estimate` |
| `rul.interval.lower_bound` | Lower conformal interval bound | Present in `RULInterval` | `predictions.lower_bound` |
| `rul.interval.upper_bound` | Upper conformal interval bound | Present in `RULInterval` | `predictions.upper_bound` |
| `rul.interval.coverage_level` | Nominal conformal coverage, e.g. 0.90 | Present | `predictions.coverage_level`; nominal target is not a per-row guarantee |
| `rul.at_cap` | Whether the displayed estimate follows the capped-RUL convention | Present in nested RUL schema | `predictions.at_cap` |
| `rul_threshold_probability.threshold_cycles` | Configured RUL threshold | Current field `horizon_cycles` | `risk_scores.rul_threshold` |
| `rul_threshold_probability.probability` | Estimated probability RUL is at or below threshold | Current field `value` | `risk_scores.rul_threshold_probability`; estimate only, not real-world failure probability |
| `risk_level` | `LOW`, `MEDIUM`, or `HIGH` | Current nested `risk.level` | `risk_scores.risk_level` |
| Risk threshold version | Provenance for risk thresholds | Nested `risk.thresholds_version` | `risk_scores.thresholds_version`; retain in response only if useful and agreed |
| `trend` | Recent trend summary | Optional string | No dedicated table/column in schema v0; omit until calculated and validated |
| `top_contributors[].feature` | Actual model input feature name | Present | SHAP output from model/explanation module; not currently persisted by schema v0 |
| `top_contributors[].shap_value` | Signed SHAP value | Current field is `contribution` | Rename field to `shap_value`; do not label as a sensor if it may be an engineered feature |
| `top_contributors[].effect_on_rul` | Optional validated plain-language direction | Not present | Include only if the direction-mapping logic is implemented and tested |
| `recommendation.summary` | Research-oriented suggested next investigation | Current `recommended_investigation` array | Derived from versioned decision rules; no dedicated recommendation table in schema v0 |
| `recommendation.rule_id` | Rule that produced the recommendation | Not present | Include when a stable rule identifier exists; otherwise omit |
| `generated_at` | UTC time the summary was assembled | Present | Application-generated; not a C-MAPSS timestamp |
| `disclaimer` | Fixed research-scope disclaimer | Missing | Include in response if the team accepts it as required; avoid repeating inconsistent variants |

### Proposed Health Summary shape

The following is a structural example only. Values are illustrative, and optional fields should be omitted when unavailable.

```json
{
  "machine_id": "FD001-E047",
  "dataset_id": "FD001",
  "cycle": 187,
  "model_version": "xgboost-v0",
  "rul": {
    "estimate": 18,
    "interval": {
      "lower_bound": 14,
      "upper_bound": 23,
      "coverage_level": 0.90
    },
    "at_cap": false
  },
  "rul_threshold_probability": {
    "threshold_cycles": 30,
    "probability": 0.81
  },
  "risk_level": "HIGH",
  "top_contributors": [
    {
      "feature": "sensor_11_rolling_mean_5",
      "shap_value": 2.4,
      "effect_on_rul": "decreases_estimated_rul"
    }
  ],
  "recommendation": {
    "summary": "Inspect the relevant subsystem",
    "rule_id": "HIGH_RISK_SENSOR_PATTERN_01"
  },
  "generated_at": "2026-10-14T10:30:00Z",
  "disclaimer": "Research-oriented decision support based on simulated C-MAPSS data and retrieved technical knowledge."
}
```

In this example, `trend` is omitted because no trend computation is shown. `effect_on_rul` should be omitted if no validated mapping exists. The probability and interval must be omitted when their generating/calibration method is not available.

## 5. Prediction record versus Health Summary

The current OpenAPI `Prediction` schema uses:
- `prediction_id`
- UUID `machine_id`
- `predicted_rul`
- optional nullable `rul_interval`
- `model_version`
- `created_at`

The database stores prediction values in `predictions`, including interval columns and `model_version_id`. This is a reasonable persistence-oriented record, but it is not identical to the composed Health Summary.

Recommended separation:
- **Prediction API record:** retain `predicted_rul` if that name is already used by the prediction endpoint; include a clear identifier convention and explicit model-version serialization.
- **Health Summary:** use the agreed `rul.estimate` field and top-level `risk_level`, with optional explanations/recommendation.
- **Mapping layer:** implement one explicit mapper from database prediction + risk + explanation/rule outputs to Health Summary. Avoid allowing frontend components to guess which field names correspond.

If the team instead decides to standardize the Prediction response on `rul.estimate`, update the request/response schemas, examples, backend code, and tests together.

## 6. Database integration notes

### Machines and sensor readings
- `machines.machine_code` is unique and should be the readable external identifier.
- `(dataset_id, engine_id)` is unique; use it to prevent duplicate registration of the same C-MAPSS engine.
- `sensor_readings` stores operating settings and sensor values in separate columns, while OpenAPI returns an object keyed by sensor name. The API serializer must map between the fixed columns and the `sensors` object.
- `sensor_readings.created_at` is an ingestion/database timestamp, not the observation time of the original C-MAPSS cycle.
- Add or retain uniqueness on `(machine_id, cycle)`; the current schema already has it.

### Predictions and model versions
- `predictions.model_version_id` is a UUID foreign key; `model_versions.version` is the human-readable version.
- The current uniqueness constraint `(machine_id, model_version_id, cycle)` prevents storing multiple predictions for the same machine/model/cycle. Confirm this is intended before adding repeated inference runs or comparing alternate feature versions.
- `lower_bound`, `upper_bound`, and `coverage_level` can be null in storage when the interval is unavailable. The API should omit `rul.interval` if unavailable, rather than expose a nullable object, if that is the accepted contract.
- The schema permits `coverage_level = 1`, while the OpenAPI interval requires a value strictly below 1. Align this constraint; nominal conformal levels should be in the agreed range, ordinarily `0 < coverage_level < 1`.
- `at_cap` is stored on the prediction and can be serialized into the RUL object.

### Risk scores
- `risk_scores` links to a prediction and stores `risk_level`, `rul_threshold`, optional threshold probability, and optional threshold-version label.
- Health Summary `rul_threshold_probability.threshold_cycles` maps to `rul_threshold`; `probability` maps to `rul_threshold_probability`.
- Do not imply that a calibrated RUL-threshold estimate is the probability of an actual real-world failure.
- If multiple risk rows can exist for a prediction, define which row is selected (for example, current configured thresholds/version). The current schema does not enforce one risk row per prediction.

### SHAP explanations, recommendations, and trend
- Schema v0 has no dedicated SHAP-contributor, trend, or recommendation table.
- For the initial vertical slice, these may be computed at request time and returned without persistence, if that choice is documented. If they must be retained for history/audit, add a versioned persistence design before implementation.
- Preserve feature names exactly as used by the model pipeline, including engineered rolling/trend features.
- SHAP values explain model output behavior; they do not establish physical causation.

### Disclaimer and provenance
- The current SQL schema has no explicit Health Summary table and no dedicated field for the fixed disclaimer.
- `generated_at` can be set by the application at summary assembly time.
- Model/data provenance should be included when available. A retrieved document citation in a conversational answer supports the retrieved claim; it does not prove that a model prediction is correct.

## 7. OpenAPI changes recommended for v0

Before implementation, align `docs/api/openapi.yaml` with these points:

1. Resolve the machine path identifier ambiguity. Recommended public path uses the readable machine code, while UUID remains internal.
2. Change `HealthSummary.machine_id` from UUID to string readable code.
3. Change `HealthSummary.rul.point` to `rul.estimate`.
4. Make `rul.interval` optional and omit it when unavailable; do not require a nullable interval.
5. Change `rul_threshold_probability.horizon_cycles` to `threshold_cycles`, and `value` to `probability`. Decide separately whether method/provenance metadata is needed.
6. Replace nested `risk.level` with top-level `risk_level`. Preserve threshold-version provenance only if the team wants it in the API.
7. Change contributor field `contribution` to `shap_value`; optionally define `effect_on_rul` only after its mapping is validated.
8. Replace `recommended_investigation` array with optional `recommendation` object containing `summary` and optionally `rule_id`.
9. Decide whether `generated_at` and `disclaimer` are required. If required, add both to schema and examples; if not, define exactly when each is omitted.
10. Keep the Prediction record schema distinct from Health Summary, and document the mapping.
11. Align the database `coverage_level` constraint with OpenAPI's strict upper bound below 1.
12. Add schema examples and contract tests for both complete and minimal valid summaries.

These are recommendations, not yet edits to `openapi.yaml`.

## 8. Runtime and deployment boundary

The current `docker-compose.yml` defines only a PostgreSQL 16 service, exposed on host port 5433, with a named data volume and readiness check. It does not currently define FastAPI, React, MLflow, a vector extension, or an LLM service.

Therefore:
- Describe Compose today as the database development environment only.
- Add backend/frontend services in a separate implementation change when their Dockerfiles and environment configuration exist.
- Do not claim pgvector is enabled: the current SQL schema enables `pgcrypto`, not a vector extension.
- The Compose file contains a development database password. Keep it local-only; use environment variables/secrets for shared or deployed environments.
- A future FastAPI service should load/use the model inside the backend process for the planned first deployment, rather than introducing a separate ML microservice by default.

## 9. Contract tests and acceptance checklist

Implement tests before declaring the contract stable:

- [ ] Readable `machine_id` accepts codes like `FD001-E047`; internal UUIDs never leak into this field.
- [ ] `dataset_id` accepts only FD001–FD004.
- [ ] `cycle` is a positive integer and is never treated as a timestamp.
- [ ] Required RUL estimate is non-negative.
- [ ] Interval lower bound is non-negative and does not exceed upper bound.
- [ ] Interval `coverage_level` is between 0 and 1 exclusive.
- [ ] Missing interval is omitted, not fabricated.
- [ ] Probability is between 0 and 1 inclusive and clearly describes the RUL-threshold estimate.
- [ ] `risk_level` is one of LOW, MEDIUM, HIGH when risk classification is available and included.
- [ ] SHAP contributors use `feature` and `shap_value`; optional direction labels only appear when validated.
- [ ] Optional trend/recommendation/probability/interval fields are omitted when unavailable.
- [ ] `generated_at` is an application-generated UTC timestamp.
- [ ] Disclaimer text is consistent with the agreed research scope.
- [ ] Database-to-API mapping is covered by tests, including readable machine code and model version joins.
- [ ] OpenAPI schema validation runs in CI when the contract is updated.

## 10. Decisions still requiring team confirmation

1. **Public machine path:** readable code (recommended) or UUID with the name `machine_uuid`.
2. **Health Summary required fields:** recommended minimum is `machine_id`, `dataset_id`, `cycle`, `model_version`, `rul.estimate`, and `generated_at`; require `risk_level` only once risk classification is implemented and included. Decide whether the disclaimer is required in every response.
3. **Persistence of explanations:** compute at request time for v0 or add a table for stored SHAP values and decision-rule outputs.
4. **Model version display:** whether `model_version` is only `model_versions.version` or a composite including model name and dataset.
5. **Risk row selection:** define behavior when several risk-score rows exist for one prediction.
6. **Repeated predictions:** decide whether the current unique constraint is retained or expanded to include an inference/run identifier.
7. **Probability method metadata:** whether the Health Summary includes method/version provenance for the RUL-threshold estimate.

Until these are resolved, avoid silently changing the schema or presenting optional capabilities as implemented.
