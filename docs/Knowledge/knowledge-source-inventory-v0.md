# Knowledge Source Inventory v0

**Project:** Conversational Predictive Maintenance and Decision Support System  
**Status:** Proposed source inventory for M0  
**Version:** v0  
**Purpose:** Identify, classify, and track technical sources for the knowledge retrieval and conversational maintenance-assistance modules.

---

## 1. Purpose

The system will use Retrieval-Augmented Generation (RAG) to retrieve relevant technical information and provide context-grounded explanations alongside machine-health predictions.

This inventory defines the source categories required to support:

- Sensor-to-component mapping.
- Potential degradation mechanisms associated with sensor behavior.
- Remaining Useful Life (RUL) and predictive maintenance concepts.
- Model interpretation and uncertainty communication.
- Maintenance decision-support rules and their supporting evidence.
- Evaluation of retrieval quality and answer grounding.

This is an initial inventory, not a claim that every source has been collected, reviewed, indexed, or integrated into the application.

## 2. Knowledge Boundaries

The knowledge base must distinguish between three types of information:

1. **Dataset evidence:** Information directly available from the NASA C-MAPSS dataset, including operating settings, sensor measurements, engine identifiers, and operating cycles.
2. **Technical knowledge:** Information from authoritative documentation and research literature about prognostics, degradation mechanisms, sensor interpretation, and predictive maintenance.
3. **Project-defined decision rules:** Explicit rules created by the team to translate model outputs and selected explanatory features into research-oriented investigation suggestions.

These categories must not be treated as interchangeable.

A sensor feature identified by SHAP indicates influence on the model's output. It does not, by itself, prove that a particular physical component is damaged or that a specific degradation mechanism is occurring.

Likewise, retrieved technical documentation provides context for an answer but does not prove that an individual RUL prediction is correct.

## 3. Source Inventory

The following sources are candidates for collection and review. Their inclusion does not mean that their full contents have already been downloaded or approved for production use.

| ID | Source | Intended use | Priority | Review status |
|---|---|---|---|---|
| KS-001 | NASA Prognostics Center of Excellence C-MAPSS dataset documentation | Understand dataset structure, operating conditions, sensor data, and benchmark limitations | Critical | To review |
| KS-002 | Original or authoritative C-MAPSS dataset publication and associated technical documentation | Understand the simulation context and benchmark design | Critical | To identify and review |
| KS-003 | NASA or other authoritative prognostics documentation | Establish terminology and background for prognostics and RUL estimation | High | To identify and review |
| KS-004 | Peer-reviewed research on C-MAPSS sensor behavior and degradation modelling | Investigate published interpretations and modelling approaches | High | To identify and review |
| KS-005 | Peer-reviewed research on predictive maintenance and condition monitoring | Support general predictive maintenance concepts | High | To identify and review |
| KS-006 | SHAP official documentation and foundational publication | Explain feature attribution and limitations | High | To review |
| KS-007 | Conformal prediction research and implementation documentation | Explain prediction intervals, calibration, and coverage evaluation | High | To review |
| KS-008 | Peer-reviewed research on sensor-to-component relationships and degradation mechanisms | Support carefully qualified technical explanations | High | To identify and review |
| KS-009 | Project-defined risk thresholds and decision-rule specification | Map risk levels and explanatory feature patterns to investigation suggestions | Critical | To author and review |
| KS-010 | Project evaluation questions and expected-answer references | Evaluate retrieval relevance, grounding, and answer consistency | Critical | To create |

## 4. Recommended Starting References

Use the following official or primary-source starting points when collecting documents.

### 4.1 NASA C-MAPSS dataset

**Source:** NASA Prognostics Center of Excellence Data Repository

URL: https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository/

Purpose:
- Establish the official dataset source.
- Review available dataset documentation.
- Record the limitations of the simulated turbofan-engine case study.
- Identify which details are documented by NASA and which are inferred from secondary literature.

The project should use FD001 first for the initial end-to-end implementation, then evaluate FD002, FD003, and FD004 under the agreed experimental protocol.

### 4.2 SHAP documentation

**Source:** SHAP documentation

URL: https://shap.readthedocs.io/

Purpose:
- Understand local and global feature attribution.
- Document how SHAP values relate to the model output being explained.
- Explain why attribution is not equivalent to physical causation.

The team must record the model output and explainer configuration used when generating SHAP values.

### 4.3 Conformal prediction

**Source:** Conformal prediction foundational research and relevant implementation documentation.

A starting point for research is:

Angelopoulos, A. N., and Bates, S. (2023). *Conformal Prediction: A Gentle Introduction.*

URL: https://arxiv.org/abs/2107.07511

Purpose:
- Understand calibration and prediction-set or interval construction.
- Explain the meaning of a nominal coverage level.
- Design held-out-engine coverage and interval-width evaluation.

The team must distinguish nominal conformal coverage from a guarantee that applies to an individual machine prediction. The project's evaluation must document assumptions and empirical results.

### 4.4 Additional primary research

For C-MAPSS-specific technical interpretations, locate the original dataset publications and peer-reviewed studies that explicitly describe the relevant simulation, operating conditions, sensor variables, or degradation mechanisms.

Do not create a sensor-to-component mapping solely from an undocumented internet table or a model-generated explanation.

For every technical source selected, record its title, authors, publication year, source URL or DOI, and the exact claims it supports.

## 5. Sensor-to-Component and Degradation Knowledge

A central objective is to connect influential model features with relevant technical context without claiming more than the evidence supports.

The proposed knowledge table should contain the following fields:

| Field | Description |
|---|---|
| `knowledge_id` | Stable identifier for the knowledge entry |
| `dataset_id` | Applicable C-MAPSS subset, if relevant |
| `sensor_or_feature` | Raw sensor or engineered feature name |
| `component` | Component or subsystem discussed by the source |
| `degradation_mechanism` | Mechanism described by the source |
| `operating_context` | Conditions or limitations under which the interpretation applies |
| `source_id` | Identifier of the supporting source |
| `source_location` | Page, section, table, figure, or paragraph reference |
| `evidence_quote_or_summary` | Short supporting extract or faithful summary |
| `confidence_status` | Evidence-review status, not model confidence |
| `reviewer_notes` | Caveats, conflicting evidence, or unresolved questions |

### Evidence-review status

Use controlled values such as:

- `UNREVIEWED` — source has not yet been checked.
- `SUPPORTED` — the cited source explicitly supports the entry.
- `QUALIFIED` — the source supports a narrower claim or requires important caveats.
- `CONFLICTING` — sources disagree or the interpretation is unresolved.
- `REJECTED` — insufficient evidence or an unsupported interpretation.

These statuses describe the team's evidence review. They are not probabilities and must not be presented as statistical confidence scores.

### Important limitation

Do not assume that every C-MAPSS sensor maps one-to-one to a physical component or a single degradation mechanism. Some sensor relationships may be indirect, simulated, operating-condition-dependent, or insufficiently documented.

If no reliable mapping can be found, record the entry as unresolved rather than inventing a relationship.

## 6. Decision-Rule Knowledge

Decision rules should be authored separately from source-derived technical knowledge.

A proposed rule record should include:

| Field | Description |
|---|---|
| `rule_id` | Stable rule identifier |
| `rule_version` | Version of the rule |
| `risk_level` | Applicable risk band |
| `rul_threshold_cycles` | Optional RUL threshold used by the rule |
| `required_feature_conditions` | Explicit conditions, if any |
| `investigation_suggestion` | Research-oriented action or question |
| `supporting_source_ids` | Sources supporting the technical rationale |
| `limitations` | Conditions where the rule should not be applied |
| `status` | Draft, reviewed, approved, or retired |

Rules must be deterministic and testable where possible. They should not silently convert SHAP rankings into diagnoses.

For example, a rule may recommend reviewing a particular sensor trend when the model assigns a high-risk band and that feature is influential. It must not claim that the corresponding component has failed unless independently supported evidence establishes that conclusion.

Risk thresholds and rule versions should be recorded so that historical outputs can be interpreted against the rules that generated them.

## 7. Retrieval Metadata Requirements

Every indexed document or knowledge entry should preserve enough metadata to trace a generated answer back to its source.

Recommended metadata:

- `source_id`
- Document title
- Author or issuing organization
- Publication year or document date, if available
- Canonical URL or DOI
- Document type
- Dataset or domain applicability
- Section, page, table, or figure reference, when available
- Collection date
- Review status
- Document version or revision, if available
- Chunk identifier
- Parent document identifier

Where licensing and storage rules permit, retain the source document or a local copy. Otherwise, retain bibliographic metadata and permitted excerpts.

The implementation should not discard source metadata when splitting documents into retrieval chunks.

## 8. RAG Answer-Grounding Rules

The conversational assistant must follow these rules:

1. Retrieve relevant passages before making source-dependent technical claims.
2. Provide citations or source references for retrieved technical claims.
3. Distinguish dataset facts, published technical claims, and project-defined rules.
4. State when the available knowledge base does not contain enough evidence.
5. Never invent a source, quotation, page number, component mapping, or maintenance procedure.
6. Do not present SHAP attribution as proof of physical causation.
7. Do not present an estimated RUL-threshold probability as a guaranteed or ground-truth probability of real-world failure.
8. Do not change the model's RUL estimate or risk level through unsupported free-form LLM reasoning.
9. Keep the model output and retrieved evidence separate in the response structure.
10. Preserve limitations and uncertainty from the underlying sources.

The LLM should explain and contextualize the available outputs, not independently fabricate a different prediction.

## 9. Knowledge-Base Evaluation Plan

Before claiming that RAG provides reliable maintenance assistance, create a small reviewed evaluation set.

The initial target is **30–50 questions**, subject to team capacity.

Include questions covering:

- Dataset and C-MAPSS limitations.
- RUL estimate interpretation.
- Conformal interval and coverage interpretation.
- Risk-band and RUL-threshold definitions.
- SHAP feature-attribution interpretation.
- Sensor-to-component knowledge when supported by sources.
- Decision-rule explanations.
- Questions for which the correct response is that evidence is insufficient.
- Questions that combine model outputs with retrieved technical context.
- Questions containing incorrect assumptions that the assistant should correct.

For each question, record:
- Expected answer or key required points.
- Relevant source IDs and passages.
- Whether abstention is expected.
- Required numerical values, if any.
- Known limitations or ambiguity.
- Review status.

### Evaluation dimensions

Evaluate at least:

- **Retrieval relevance:** whether retrieved passages are relevant to the question.
- **Source grounding:** whether claims are supported by retrieved evidence.
- **Citation correctness:** whether citations point to the material supporting the associated claim.
- **Answer completeness:** whether the response covers the expected key points.
- **Abstention behavior:** whether the assistant acknowledges missing evidence.
- **Numerical consistency:** whether quoted RUL and risk values match the supplied Machine Health Summary.
- **Scope compliance:** whether the response avoids unsupported diagnosis and real-world performance claims.

Use a manually reviewed baseline before automating evaluation. Do not treat a single aggregate score as proof that the assistant is safe for industrial use.

## 10. Relationship to the Machine Health Summary

The Machine Health Summary is the structured source of truth for prediction values supplied to the conversational layer.

The assistant must preserve the supplied values and their meanings:

- `machine_id` is the readable machine code.
- `dataset_id` identifies the C-MAPSS subset.
- `cycle` is the observed operating-cycle index.
- `rul.estimate` is the model's point estimate in cycles.
- `rul.interval` is an optional conformal interval.
- `rul_threshold_probability` is an optional estimate for the configured RUL threshold.
- `risk_level` is the system's configured risk category.
- `top_contributors` contains actual model features and SHAP values when available.
- `recommendation` contains project-defined decision support when available.

If a field is missing, the assistant must not infer an exact value merely to make the response sound complete.

Retrieved citations support the associated knowledge claims. They are not proof that the prediction itself is correct.

## 11. Collection and Review Workflow

For each source:

1. Identify the original or authoritative publication.
2. Record the bibliographic metadata and URL or DOI.
3. Confirm that the source is accessible and relevant to the intended claim.
4. Extract only the portions needed for the project.
5. Record page, section, table, or figure references where possible.
6. Draft knowledge entries with explicit limitations.
7. Have a team member review the interpretation.
8. Mark the source and entries with the appropriate review status.
9. Add approved material to the retrieval corpus.
10. Add representative questions to the RAG evaluation set.
11. Re-review entries when sources or rules change.

For any claim that materially affects a recommendation, require stronger evidence and clearer provenance than for general background explanations.

## 12. M0 Acceptance Checklist

- [ ] Initial source categories are documented.
- [ ] Official C-MAPSS dataset documentation has been located.
- [ ] SHAP documentation has been identified.
- [ ] Conformal prediction background material has been identified.
- [ ] A source metadata template has been agreed.
- [ ] A sensor-to-component knowledge-table structure has been agreed.
- [ ] A decision-rule record structure has been agreed.
- [ ] RAG grounding and abstention rules have been documented.
- [ ] A 30–50-question evaluation-set plan has been recorded.
- [ ] The team understands that source inventory does not imply source review or system integration.
- [ ] Unsupported sensor mappings and physical diagnoses are explicitly prohibited.

## 13. Out of Scope for This Inventory

This document does not claim that the team has:
- Collected and verified every listed publication.
- Completed the sensor-to-component mapping.
- Built or embedded the vector index.
- Selected or integrated the final LLM provider.
- Validated maintenance recommendations for real industrial equipment.
- Established that simulated C-MAPSS results generalize to other machine types.

Those activities must be tracked separately and marked complete only after evidence and tests are available.

---

**Research-scope disclaimer:** Research-oriented decision support based on simulated C-MAPSS data and retrieved technical knowledge.
