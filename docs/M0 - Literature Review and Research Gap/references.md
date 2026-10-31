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

5. Lundberg, S.M., Lee, S.I. (2017). A Unified Approach to Interpreting Model Predictions. Advances in Neural Information Processing Systems 30 (NeurIPS 2017). arXiv:1705.07874 (DOI 10.48550/arXiv.1705.07874). NeurIPS proceedings papers have no publisher DOI.

Dataset / topic relevance: Foundational SHAP paper.

6. Balasubramani, P., Shi, Q., DeLaurentis, D. (2024). Explainable Machine Learning for Turbojet Engine Prognostic Health Management. AIAA SciTech 2024 Forum, p. 0762. DOI: 10.2514/6.2024-0762.

Dataset / topic relevance: SHAP on turbofan PHM.

7. Lin, K.Y., Hong, Y.H., Li, M.H., Shi, Y., Matsuno, K. (2025). Predictive maintenance in industrial systems: an XGBoost-based approach for failure time estimation and resource optimization. Journal of Industrial and Production Engineering. DOI: 10.1080/21681015.2025.2519369.

Dataset / topic relevance: XGBoost + SHAP for PdM.

8. Alomari, Y., Andó, M., Baptista, M.L. (2023). Advancing aircraft engine RUL predictions: an interpretable integrated approach of feature engineering and aggregated feature importance. Scientific Reports, 13, 13466. DOI: 10.1038/s41598-023-40315-1.

Dataset / topic relevance: Interpretable RUL on C-MAPSS.

9. Lewis, P., Perez, E., Piktus, A., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Advances in Neural Information Processing Systems 33 (NeurIPS 2020). arXiv:2005.11401 (DOI 10.48550/arXiv.2005.11401). NeurIPS proceedings papers have no publisher DOI.

Dataset / topic relevance: Foundational RAG paper.

10. Harbola, C., Purwar, A.(2025). Prescriptive Agents based on RAG for Automated Maintenance (PARAM). arXiv:2508.04714.

Dataset / topic relevance:RAG + LLM for maintenance.

11. Cummins, L., Sommers, A., Ramezani, S.B., Mittal, S., Jabour, J., Seale, M., Rahimi, S. (2024). Explainable Predictive Maintenance: A Survey of Current Methods, Challenges and Opportunities. IEEE Access, 12, 57574–57602. DOI: 10.1109/ACCESS.2024.3391130. (Preprint: arXiv:2401.07871.)

Dataset / topic relevance: XAI-in-PdM survey.

12. Shafer, G., Vovk, V. (2008). A tutorial on conformal prediction. Journal of Machine Learning Research (JMLR), 9, 371–421. URL: https://jmlr.org/papers/v9/shafer08a.html (JMLR assigns no DOI). Preprint: arXiv:0706.3188.

Dataset / topic relevance: Foundational CP tutorial.

13. Springer. (2026). A Generative AI Framework for Smart Maintenance: Utilizing RAG… Springer LNCS. DOI: 10.1007/978-3-032-03725-1_13.

Dataset / topic relevance: RAG over CMMS + manual for maintenance Q&A.

Supporting References

14. Jardine, A.K.S., Lin, D., Banjevic, D. (2006). A review on machinery diagnostics and prognostics implementing condition-based maintenance. Mechanical Systems and Signal Processing, 20(7), 1483–1510. DOI: 10.1016/j.ymssp.2005.09.012.

Dataset / topic relevance:Foundational PdM survey.

15. Lei, Y., Li, N., Guo, L., Li, N., Yan, T., Lin, J. (2018). Machinery health prognostics: A systematic review from data acquisition to RUL prediction. Mechanical Systems and Signal Processing, 104, 799–834. DOI: 10.1016/j.ymssp.2017.11.016.

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

20. Frederick, D.K., DeCastro, J.A., Litt, J.S. (2007). User's Guide for the Commercial Modular Aero-Propulsion System Simulation (C-MAPSS). NASA/TM-2007-215026. NASA Technical Reports Server: https://ntrs.nasa.gov/citations/20070034949.

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

Verification status (checked 21 October 2026)

Identifiers confirmed against the publisher, DOAJ, arXiv, JMLR or NASA NTRS pages: entries 5, 9, 11, 12, 14, 15 and 20. Two author lists were wrong in the earlier draft and are corrected: entry 9 (the authors are Lewis, Perez, Piktus and others) and entry 11 (the first authors are Logan Cummins and Alexander Sommers).

Still to verify manually before the final report:

Entry 13 (Springer, 2026): the author names are missing; replace the publisher name with the authors and check the DOI.

Entry 16 (IJRASET, 2026): the venue has weak peer-review standing. Keep it only as a pointer to related work and do not use it as the sole support for a claim.

Entry 17 (Masand et al., 2025): full bibliographic details and DOI.

Entries 1 to 4, 6 to 8 and 10: their DOIs and arXiv numbers were not re-checked in this pass.

Exact metrics and operating conditions for Balasubramani et al. (2024), and the FD002/FD004 operating-condition counts in Saxena et al. (2008).