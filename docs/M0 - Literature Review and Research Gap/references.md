References

Core References

1. Saxena, A., Goebel, K., Simon, D., Eklund, N. (2008). Damage propagation modeling for aircraft engine run-to-failure simulation. PHM08. DOI: 10.1109/PHM.2008.4711414.

Dataset / topic relevance: Defines C-MAPSS FD001–FD004 benchmark.

2. Ramasso, E., Saxena, A. (2014). Performance Benchmarking and Analysis of Prognostic Methods for CMAPSS Datasets. International Journal of Prognostics and Health Management (IJPHM), 5(2), 1–15. HAL: hal-01324587.

Dataset / topic relevance: Benchmarking guidelines for C-MAPSS RUL.

3. Javanmardi, A., Hüllermeier, E. (2023). Conformal Prediction Intervals for Remaining Useful Lifetime Estimation. IJPHM, 14(2). DOI: 10.36001/ijphm.2023.v14i2.3417.

Dataset / topic relevance: Split conformal prediction for C-MAPSS RUL.

4. Robinson, M.(2026). Remaining Useful Life Estimation for Aircraft Engines with Risk-Aware Prediction Intervals via Conformalized Quantile Regression. IJPHM, 17(1). DOI: 10.36001/ijphm.2026.v17i1.4724.

Dataset / topic relevance: Risk-aware CQR intervals on C-MAPSS.

5. Lundberg, S.M., Lee, S.I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS 2017. DOI not verified.

Dataset / topic relevance: Foundational SHAP paper.

6. Balasubramani, P., Shi, Q., DeLaurentis, D. (2024). Explainable Machine Learning for Turbojet Engine Prognostic Health Management. AIAA SciTech 2024 Forum, p. 0762. DOI: 10.2514/6.2024-0762.

Dataset / topic relevance: SHAP on turbofan PHM.

7. Lin, K.Y., Hong, Y.H., Li, M.H., Shi, Y., Matsuno, K. (2025). Predictive maintenance in industrial systems: an XGBoost-based approach for failure time estimation and resource optimization. Journal of Industrial and Production Engineering. DOI: 10.1080/21681015.2025.2519369.

Dataset / topic relevance: XGBoost + SHAP for PdM.

8. Alomari, Y., Andó, M., Baptista, M.L. (2023). Advancing aircraft engine RUL predictions: an interpretable integrated approach of feature engineering and aggregated feature importance. Scientific Reports, 13, 13466. DOI: 10.1038/s41598-023-40315-1.

Dataset / topic relevance: Interpretable RUL on C-MAPSS.

9. Lewis, P., Guu, K., Lomeli, M., et al.(2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020. DOI not verified.

Dataset / topic relevance: Foundational RAG paper.

10. Harbola, C., Purwar, A.(2025). Prescriptive Agents based on RAG for Automated Maintenance (PARAM). arXiv:2508.04714.

Dataset / topic relevance:RAG + LLM for maintenance.

11.Cummins, J., Sommers, T. (2024). Explainable Predictive Maintenance: A Survey of Current Methods, Challenges and Opportunities. arXiv:2401.07871 / IEEE Access. DOI not verified.

Dataset / topic relevance: XAI-in-PdM survey.

12. Shafer, G., Vovk, V. (2008). A tutorial on conformal prediction. Journal of Machine Learning Research (JMLR), 9, 371–421. DOI not verified.

Dataset / topic relevance: Foundational CP tutorial.

13. Springer. (2026). A Generative AI Framework for Smart Maintenance: Utilizing RAG… Springer LNCS. DOI: 10.1007/978-3-032-03725-1_13.

Dataset / topic relevance: RAG over CMMS + manual for maintenance Q&A.

Supporting References

14. Jardine, A.K.S., Lin, D., Banjevic, D.(2006). A review on machinery diagnostics and prognostics implementing condition-based maintenance. Mechanical Systems and Signal Processing. DOI not verified.

Dataset / topic relevance:Foundational PdM survey.

15. Lei, Y., Li, N., Guo, L., et al. (2018). Machinery health prognostics: A systematic review from data acquisition to RUL prediction. Mechanical Systems and Signal Processing. DOI not verified.

Dataset / topic relevance:Comprehensive RUL review.

16. IJRASET. (2026). Trustworthy Remaining Useful Life Prediction on NASA C-MAPSS: Coupling Conformal Uncertainty with Audited SHAP Explanations. International Journal for Research in Applied Science and Engineering Technology. DOI not verified.

Dataset / topic relevance: RUL + CP + SHAP on C-MAPSS.

17. Masand, A., et al. (2025). Leveraging Conversational AI to Streamline Troubleshooting and Maintenance in Aviation. Springer LNNS. DOI not verified.

Dataset / topic relevance:RUL + conversation for aviation technicians.

Official / Technical Sources

18. NASA.(2025). CMAPSS Jet Engine Simulated Data. NASA Dataset Repository.

URL: https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data.

Dataset / topic relevance:Official C-MAPSS dataset description.

19.PHM Society.(2023). NASA Prognostics Center of Excellence Data Set Repository.

URL: https://data.phmsociety.org/nasa/.

Dataset / topic relevance:Mirror of NASA PCoE datasets.

20. Frederick, D., DeCastro, J., Litt, J. (2007). User's guide for C-MAPSS. NASA/TM-2007-215026. DOI not verified.

Dataset / topic relevance: C-MAPSS simulation tool documentation.

Final Research Summary

Primary research gap

No verified C-MAPSS system integrates RUL prediction, conformal uncertainty, SHAP explainability, RAG-based technical knowledge retrieval, and LLM-based conversational decision support into a single end-to-end flow. Existing studies address pairwise combinations (e.g., RUL+CP, RUL+SHAP, RAG+LLM) but rarely evaluate the full chain from prediction to grounded conversational summary.

Project contribution

This B.Tech project implements and evaluates a unified pipeline on C-MAPSS FD001–FD004: XGBoost RUL → split conformal uncertainty → threshold-based risk → SHAP with sensor-to-component mapping → RAG over technical documents → grounded LLM conversational assistant. The contribution is integration and evaluation-oriented, not algorithmic novelty.

Strongest supporting papers

Saxena et al. (2008) — C-MAPSS dataset definition.

Ramasso & Saxena (2014) — C-MAPSS benchmarking guidelines.

Javanmardi & Hüllermeier (2023) — Conformal prediction for RUL.

Robinson (2026) — Risk-aware CQR intervals.

Lundberg & Lee (2017) — SHAP foundation.

Balasubramani et al. (2024) — SHAP for turbofan PHM.

Lin et al. (2025) — XGBoost + SHAP for PdM.

Harbola & Purwar (2025) — RAG + LLM for maintenance.

Confidence in research gap

High — No verified counter-example found; multiple papers support fragmented integration.

Remaining items requiring manual verification

Exact DOI for Lundberg & Lee (2017) NeurIPS paper.

Exact DOI for Lewis et al. (2020) NeurIPS RAG paper.

Full author list and DOI for Cummins & Sommers (2024) survey.

Exact metrics and operating conditions for Balasubramani et al. (2024) AIAA paper.

Full bibliographic details for IJRASET (2026) and Masand et al. (2025) papers.

Confirm FD002/FD004 operating condition counts in Saxena et al. (2008).
