Research Gap Analysis

1. Background

Identifying a research gap is necessary to position this B.Tech project within the existing literature on predictive maintenance (PdM), Remaining Useful Life (RUL) prediction, uncertainty quantification (UQ), explainable AI (XAI), retrieval-augmented generation (RAG), and large language model (LLM)-based decision support. A well-defined gap ensures the project contributes meaningfully without over-claiming novelty.

2. Existing Research Landscape

RUL Prediction

C-MAPSS-based RUL prediction is mature, with 70+ papers benchmarked by Ramasso and Saxena (2014). Tree-based models (XGBoost, Random Forest) are competitive with deep learning [Lin et al., 2025; Alomari et al., 2023].

C-MAPSS

The NASA C-MAPSS dataset is the standard benchmark for turbofan RUL, with FD001–FD004 covering single and multiple operating conditions [Saxena et al., 2008; Ramasso & Saxena, 2014].

ML / XGBoost

XGBoost is widely used for RUL due to strong performance and SHAP compatibility [Lin et al., 2025].

Operating Conditions

FD002/FD004 require regime-aware preprocessing; cross-subset generalization is underexplored [Ramasso & Saxena, 2014].

Uncertainty

Conformal prediction (CP) provides valid RUL intervals on C-MAPSS [Javanmardi & Hüllermeier, 2023; Robinson, 2026].

SHAP / XAI

SHAP is dominant in PdM XAI; component-level mapping is limited [Balasubramani et al., 2024; Cummins & Sommers, 2024].

Sensor-Component Interpretation

Few studies systematically map SHAP-important sensors to components/degradation mechanisms [Scientific Reports, 2025].

RAG

RAG is used for maintenance Q&A over CMMS/manuals but not integrated with RUL/UQ/SHAP [Harbola & Purwar, 2025; Springer, 2026].

LLMs

LLMs are emerging for maintenance assistance but lack prognostic grounding [Masand et al., 2025].

Decision Support

Few systems integrate prediction, uncertainty, explainability, retrieval, and conversation into end-to-end decision support [IJRASET, 2026].

3. Gap Analysis by Level

Level 1 — Individual Method Gaps

RUL prediction: Well-studied; no major gap.

Uncertainty (CP):Valid intervals exist; marginal coverage limitation.

SHAP: Sensor-level importance common; component-level mapping limited.

RAG/LLM:Emerging in maintenance; not integrated with RUL/UQ/SHAP.

Level 2 — Pairwise Integration Gaps

RUL + uncertainty: Addressed by Javanmardi & Hüllermeier (2023) and Robinson (2026).

RUL + SHAP: Addressed by Balasubramani et al. (2024) and Lin et al. (2025).

RAG + LLM:Addressed by Harbola & Purwar (2025) and Springer (2026).

Prediction + decision support: Partial; few link RUL/UQ to explicit risk metrics.

Level 3 — Multi-Component Integration Gaps

No verified C-MAPSS system combines:

- RUL prediction

- Conformal uncertainty

- SHAP explainability

- RAG retrieval

- LLM conversation

into a single decision-support flow [IJRASET, 2026; Masand et al., 2025].

Level 4 — End-to-End Decision-Support Evaluation

Existing studies do not jointly evaluate:

- Numerical faithfulness (RUL ↔ LLM summary)

- Uncertainty communication (intervals ↔ risk metrics)

- Retrieval grounding (cited documents)

- Source attribution

- Hallucination resistance

- Consistency between prediction and generated answer

- Usefulness of final decision support

[Cummins & Sommers, 2024; Robinson, 2026].

4. Candidate Research Gaps

Gap 1

Gap statement:

No verified C-MAPSS system integrates RUL + conformal uncertainty + SHAP + RAG + LLM into a single decision-support flow.

Evidence from literature:

- Javanmardi & Hüllermeier (2023) and Robinson (2026) integrate RUL + CP but lack SHAP/RAG/LLM.

- Balasubramani et al. (2024) and Lin et al. (2025) integrate RUL + SHAP but lack CP/RAG/LLM.

- Harbola & Purwar (2025) and Springer (2026) integrate RAG + LLM but lack RUL/CP/SHAP.

- IJRASET (2026) links RUL + CP + SHAP but no retrieval/conversation.

Existing approaches:

Pairwise combinations (RUL+CP, RUL+SHAP, RAG+LLM).

Observed limitation:

Fragmented integration; no end-to-end flow.

Why this matters:

Technicians need simultaneous access to RUL, uncertainty, explanations, and retrieved guidance.

How our project addresses it:

Implements unified pipeline on C-MAPSS FD001–FD004.

Evidence strength:

A — Strongly supported.

Relevant papers:

[34][72][107][35][109][133][71][116][6][133][152][159][70][74][91][112]

Risk of overclaiming:

Low; no verified counter-example found.

Gap 2

Gap statement:

Conformal intervals are rarely translated into explicit maintenance risk metrics (e.g., probability RUL < threshold).

Evidence from literature:

Robinson (2026) introduces asymmetric CQR intervals but does not compute threshold-based failure probabilities.

Existing approaches:

Asymmetric CQR intervals.

Observed limitation:

No explicit P(RUL < threshold) or decision rules.

Why this matters:

Technicians need actionable risk scores, not just intervals.

How our project addresses it:

Derives P(RUL < threshold) from calibrated residuals.

Evidence strength:

B — Moderately supported.

Relevant papers:

[35][109][133][156][160]

Risk of overclaiming:

Low; Robinson (2026) supports gap.

Gap 3

Gap statement:

SHAP explanations are seldom mapped to component-level degradation mechanisms.

Evidence from literature:

Balasubramani et al. (2024) identify critical components/sensors but lack structured mapping.

Existing approaches:

SHAP feature importance.

Observed limitation:

No sensor→component→degradation ontology.

Why this matters:

Component-aware explanations are more actionable.

How our project addresses it:

Builds sensor-to-component mapping based on C-MAPSS documentation.

Evidence strength:

B — Moderately supported.

Relevant papers:

[71][116][31][6][133][134][136]

Risk of overclaiming:

Low; Balasubramani et al. (2024) supports gap.

5. Counter-Evidence

IJRASET (2026) links RUL + CP + SHAP and discusses explanation trust, but lacks retrieval/conversation. This weakens Gap 1 slightly but does not close it.

Masand et al. (2025) integrate RUL + conversation but lack CP/SHAP/RAG. This supports Gap 1.

PARAM (Harbola & Purwar, 2025) and Springer (2026) provide RAG + LLM for maintenance but lack RUL/CP/SHAP. This supports Gap 1.

No paper contradicts the claim that no verified C-MAPSS system combines all five components.

6. Recommended Primary Research Gap

Gap 1 is the strongest and most defensible:

- Supported by literature: No verified counter-example.

- Specific: Integrates five components on C-MAPSS.

- Experimentally evaluable: Can measure RUL accuracy, coverage, SHAP stability, retrieval relevance, and decision-support usefulness.

- Realistic for B.Tech: Uses established methods (XGBoost, CP, SHAP, RAG, LLM) in a novel integration.

- Aligned with implementation: Matches project architecture.

- Not dependent on absolute novelty: Focuses on integration and evaluation, not inventing new algorithms.

7. Final Research Gap Statement

Academic version (100–150 words)

Existing studies on NASA C-MAPSS-based remaining useful life (RUL) prediction largely focus on optimizing point estimates or, more recently, on adding calibrated uncertainty via conformal prediction and explainability via SHAP. A recurring limitation is that these components remain fragmented: uncertainty is rarely translated into explicit maintenance risk metrics, SHAP explanations are seldom mapped to component-level degradation mechanisms, and conversational decision-support systems typically lack integration with prognostic outputs and retrieved technical knowledge. Most evaluated approaches address pairwise combinations (e.g., RUL + uncertainty, RUL + SHAP, or RAG + LLM for maintenance Q&A), but there remains limited emphasis on end-to-end flows that connect prediction, conformal uncertainty, SHAP-based component insights, RAG-retrieved evidence, and grounded conversational summaries. This motivates an integrated framework that unifies these elements into a single decision-support prototype, explicitly scoped as a research-oriented system evaluated on simulated C-MAPSS data rather than a certified maintenance authority.

Short project-report version (50–80 words)

Existing C-MAPSS RUL studies focus on point prediction, uncertainty, or explainability in isolation. Few integrate RUL + conformal uncertainty + SHAP + RAG + LLM into a single decision-support flow. This project addresses this gap by unifying these components on FD001–FD004, with explicit risk metrics, component-level explanations, and grounded conversational summaries.

Presentation version (3–5 sentences)

Most C-MAPSS RUL research optimizes point predictions or adds uncertainty/explainability separately. Few systems integrate RUL, conformal uncertainty, SHAP, RAG, and LLM conversation into one decision-support flow. Our project unifies these components on FD001–FD004, with risk metrics, component-level explanations, and grounded conversational summaries.

One-line version

An integrated C-MAPSS RUL + conformal uncertainty + SHAP + RAG + LLM decision-support system is underexplored in the literature.
