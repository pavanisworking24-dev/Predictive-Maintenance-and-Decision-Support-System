Literature Review on a Conversational Predictive Maintenance and Decision Support System

1. Introduction

Predictive maintenance (PdM) has evolved from simple condition monitoring to data-driven prognostics that estimate the Remaining Useful Life (RUL) of critical assets such as aircraft engines, turbines, and industrial machinery [Jardine et al., 2006; Lei et al., 2018]. Modern PdM systems increasingly combine machine learning (ML) for RUL prediction, uncertainty quantification (UQ) to express confidence in predictions, explainable AI (XAI) to interpret model behavior, and knowledge retrieval to ground decisions in technical documentation [Cummins & Sommers, 2024]. More recently, large language models (LLMs) and retrieval-augmented generation (RAG) have been explored for conversational technical assistance and maintenance decision support [Lewis et al., 2020; Harbola & Purwar, 2025].

This literature review examines research across these areas with a focus on turbofan engine RUL prediction using the NASA C-MAPSS benchmark. The goal is to identify what has been established, where limitations persist, and where an integrated B.Tech-level system can make a reasonable contribution without over-claiming novelty.

2. Predictive Maintenance and Prognostics

Predictive maintenance aims to schedule maintenance based on the actual condition of equipment rather than fixed intervals, reducing downtime and costs while improving safety [Jardine et al., 2006]. Prognostics, a core component of PdM, involves estimating the future health state of a system and predicting its RUL—the time until a predefined failure threshold is reached [Lei et al., 2018].

Early PdM research focused on statistical models and physics-based degradation modeling. More recent work emphasizes data-driven ML methods that learn degradation patterns from sensor time series [Ramasso & Saxena, 2014]. While many studies achieve accurate RUL estimates, a recurring limitation is the weak coupling between prognostic outputs and maintenance decision logic. Uncertainty is often under-reported, and explanations rarely connect to component-level degradation mechanisms or actionable maintenance guidance [Cummins & Sommers, 2024; Robinson, 2026].

3. NASA C-MAPSS and RUL Prediction

The NASA Commercial Modular Aero-Propulsion System Simulation (C-MAPSS) dataset is the de facto benchmark for turbofan engine RUL prediction [Saxena et al., 2008]. It contains simulated run-to-failure trajectories for multiple engines under varying operating conditions and fault modes. The dataset is split into four subsets: FD001 and FD003 (single operating condition) and FD002 and FD004 (multiple operating conditions) [Ramasso & Saxena, 2014].

C-MAPSS is widely used because it provides multivariate sensor data, known RUL labels, and a realistic simulation of degradation processes. However, it is simulated data, not real aircraft telemetry, and results do not directly imply operational performance [Saxena et al., 2008]. Common evaluation metrics include MAE, RMSE, R², and the PHM08 asymmetric scoring function, which penalizes late predictions more heavily [Ramasso & Saxena, 2014].

A key limitation identified by Ramasso and Saxena (2014) is inconsistent preprocessing and metric reporting across studies, hindering fair comparison. Many papers focus on FD001 only, while FD002–FD004 are underutilized. Cross-subset generalization is rarely analyzed systematically.

4. Machine Learning for RUL Prediction

Traditional statistical approaches (e.g., linear regression, ARIMA) have been supplemented by ML methods such as Random Forest (RF), gradient boosting (XGBoost, LightGBM), and deep learning (CNN, LSTM, GRU, transformers) [Lei et al., 2018]. Tree-based models remain competitive on C-MAPSS, often matching or exceeding deep learning performance while offering better interpretability [Lin et al., 2025; Alomari et al., 2023].

Feature engineering is critical: sliding windows, temporal degradation features, and sensor selection (e.g., via tsfresh or domain knowledge) improve model accuracy [Alomari et al., 2023]. XGBoost is frequently used due to its strong performance, handling of non-linear relationships, and compatibility with SHAP for explainability [Lin et al., 2025].

However, most studies optimize point-prediction accuracy and under-treat uncertainty and decision risk. Interpretability often stops at feature importance without connecting to component-level degradation or maintenance actions [Cummins & Sommers, 2024].

5. Operating Conditions and Cross-Condition Generalization

FD002 and FD004 contain multiple operating conditions (e.g., altitude, Mach number, throttle resolver angle), which affect sensor distributions and degradation trajectories [Saxena et al., 2008]. Operating-condition-aware preprocessing (e.g., clustering, normalization per regime) is common but not universal [Ramasso & Saxena, 2014].

Some studies evaluate cross-subset generalization explicitly, but many focus on within-subset performance only [Ramasso & Saxena, 2014]. Distribution shift between operating conditions remains challenging, and few works analyze how generalization behavior relates to uncertainty or explainability changes [Javanmardi & Hüllermeier, 2023].

This gap motivates regime-aware normalization and separate model training per subset, as well as systematic cross-subset evaluation in our project.

6. Uncertainty Quantification in RUL Prediction

Point predictions alone are insufficient for safety-critical maintenance; uncertainty quantification (UQ) is essential to express confidence and support risk-aware decisions [Robinson, 2026]. Methods include Bayesian approaches, ensemble variance, Monte Carlo dropout, and conformal prediction (CP) [Javanmardi & Hüllermeier, 2023].

Conformal prediction provides distribution-free, finite-sample coverage guarantees for prediction intervals, making it attractive for RUL estimation [Shafer & Vovk, 2008]. Javanmardi and Hüllermeier (2023) apply split CP to C-MAPSS RUL with CNN and gradient boosting, showing valid intervals. Robinson (2026) extends this with asymmetric conformalized quantile regression (CQR) to align intervals with aerospace risk preferences.

A limitation is that CP guarantees marginal (average) coverage, not conditional coverage per engine state. Few studies map intervals to explicit maintenance risk thresholds or decision rules [Robinson, 2026].

7. Explainable AI and SHAP for Predictive Maintenance

Explainable AI (XAI) is increasingly used in PdM to build trust and support maintenance decisions [Cummins & Sommers, 2024]. SHAP (SHapley Additive exPlanations) is the dominant XAI method due to its theoretical grounding and efficiency for tree-based models [Lundberg & Lee, 2017].

SHAP assigns each feature an importance value for a particular prediction, unifying several attribution methods under a game-theoretic framework. Balasubramani et al. (2024) apply SHAP to turbofan engine PHM, identifying critical sensors and components. Lin et al. (2025) pair XGBoost with SHAP for interpretable failure time estimation.

Limitations include:

(1) SHAP explains feature contributions but does not inherently map to physical degradation mechanisms.

(2) sensor-level explanations are harder to act on than component-level narratives.

(3) correlation between sensors can complicate interpretation [Cummins & Sommers, 2024].

8. Sensor, Component, and Degradation Knowledge

While SHAP identifies important sensors, systematic mappings from sensors to engine components (e.g., fan, high-pressure compressor, turbine) and degradation mechanisms (e.g., fouling, erosion, fatigue) remain limited [Balasubramani et al., 2024]. Some studies qualitatively link sensors to components, but few provide structured, retrievable knowledge connecting sensors → components → maintenance actions [Scientific Reports, 2025].

This gap motivates our project's sensor-to-component mapping based on C-MAPSS documentation and technical literature, enabling explanations such as "Sensor 11 suggests degradation in the high-pressure compressor" rather than only "Sensor 11 is important."

9. Knowledge Retrieval and RAG

Retrieval-augmented generation (RAG) combines parametric LLM memory with non-parametric retrieval from external knowledge bases, improving factual accuracy in knowledge-intensive tasks [Lewis et al., 2020]. In maintenance, RAG is used over computerized maintenance management system (CMMS) records and operational manuals for Q&A and prescriptive recommendations [Springer, 2026; Harbola & Purwar, 2025].

RAG improves grounding but does not eliminate hallucination risk; retrieved documents must be cited, and LLM outputs should be constrained to advisory roles [Cummins & Sommers, 2024]. Most RAG-PdM prototypes focus on fault classification or Q&A, not integration with quantitative RUL, uncertainty, and SHAP [Harbola & Purwar, 2025].

10. LLM-Based Conversational Decision Support

LLMs are being applied to industrial maintenance for anomaly explanation, work-instruction generation, and prescriptive recommendations [Harbola & Purwar, 2025]. Some systems serialize sensor data into natural language for LLM processing, while others use RAG to retrieve procedures before generating step-by-step guidance [Springer, 2026].

Limitations include hallucination, numerical inconsistency, lack of domain grounding, and blurred boundaries between advisory and autonomous control [Cummins & Sommers, 2024]. Few systems integrate LLMs with formal uncertainty/risk metrics or SHAP-based explanations [Masand et al., 2025].

11. Integrated Predictive Maintenance Decision Support

End-to-end PdM platforms increasingly combine prediction, dashboards, and some explainability [Robinson, 2026]. A few prototypes add GenAI explanation layers over ML outputs, but none expose the full chain:

RUL → uncertainty → risk → SHAP → retrieved knowledge → LLM explanation [IJRASET, 2026; Harbola & Purwar, 2025].

Robinson (2026) unifies point RUL estimation and risk-aware UQ but lacks explainability and conversation. PARAM (Harbola & Purwar, 2025) and Springer (2026) provide RAG + LLM for maintenance Q&A but lack RUL, CP, and SHAP. IJRASET (2026) links RUL + CP + SHAP but no retrieval or conversation.

This suggests an integration gap: no verified C-MAPSS system combines all five components in one decision-support flow.

12. Critical Synthesis

1.What has been solved reasonably well?

C-MAPSS benchmarking, RUL prediction with ML/XGBoost, split CP for uncertainty, and SHAP for explainability are well-established [Ramasso & Saxena, 2014; Javanmardi & Hüllermeier, 2023; Lin et al., 2025].

2.What remains difficult?

Cross-subset generalization, component-level interpretation of SHAP, and coupling uncertainty with decision risk are underexplored [Robinson, 2026; Cummins & Sommers, 2024].

3.Recurring limitations:

- Weak coupling between prognostics and maintenance decision logic.

- Sensor-level (not component-level) explanations.

- Fragmented integration of RUL, UQ, XAI, RAG, and LLM.

4.Separate treatment:

Prediction, uncertainty, explainability, retrieval, and conversation are often studied in isolation or pairwise combinations, not as an integrated flow [IJRASET, 2026; Masand et al., 2025].

5.Evaluation gaps:

Few studies evaluate numerical faithfulness, uncertainty communication, retrieval grounding, and decision-support usefulness jointly [Cummins & Sommers, 2024].

6.Realistic B.Tech gap:

An integration and evaluation-oriented project that unifies RUL + CP + SHAP + RAG + LLM on C-MAPSS, with explicit decision-support scoping, is defensible.

13. Research Gap

Existing studies on NASA C-MAPSS-based RUL prediction largely focus on optimizing point estimates or, more recently, on adding calibrated uncertainty via conformal prediction and explainability via SHAP. A recurring limitation is that these components remain fragmented: uncertainty is rarely translated into explicit maintenance risk metrics, SHAP explanations are seldom mapped to component-level degradation mechanisms, and conversational decision-support systems typically lack integration with prognostic outputs and retrieved technical knowledge. Most evaluated approaches address pairwise combinations (e.g., RUL + uncertainty, RUL + SHAP, or RAG + LLM for maintenance Q&A), but there remains limited emphasis on end-to-end flows that connect prediction, conformal uncertainty, SHAP-based component insights, RAG-retrieved evidence, and grounded conversational summaries. This motivates an integrated framework that unifies these elements into a single decision-support prototype, explicitly scoped as a research-oriented system evaluated on simulated C-MAPSS data rather than a certified maintenance authority.

14. Proposed Research Direction

Our project responds to this gap by implementing a unified pipeline on C-MAPSS FD001–FD004:

C-MAPSS RUL prediction -- with Linear Regression, Random Forest, and XGBoost baselines.

Split conformal prediction -- for calibrated uncertainty intervals.

Risk estimation -- based on predicted RUL and calibrated residuals (e.g., probability RUL < threshold).

SHAP-based explainability -- with sensor-to-component mapping.

RAG-based technical knowledge retrieval -- over sensor/component/degradation documents.

Grounded LLM conversational assistant -- that summarizes RUL, uncertainty, risk, and SHAP insights with citations.

Machine Health Summary -- combining all components into a single dashboard and conversational interface.

Integrated evaluation -- of MAE, RMSE, R², PHM08 score, coverage, interval width, SHAP stability, retrieval relevance, and decision-support usefulness.

This is an integration and evaluation-oriented B.Tech research project, not a claim of inventing every individual technique.

15. Conclusion

The literature on C-MAPSS-based RUL prediction is mature for individual methods (ML/XGBoost, CP, SHAP) but fragmented in integration. Uncertainty is rarely linked to decision risk, explanations seldom reach component level, and conversational systems lack prognostic grounding. Our project addresses these gaps by unifying prediction, uncertainty, explainability, retrieval, and conversation into a single decision-support prototype, evaluated systematically across all four C-MAPSS subsets. This contributes a well-documented, research-oriented platform that demonstrates how modern ML, UQ, XAI, RAG, and LLMs can work together for predictive maintenance decision support on a standard benchmark.
