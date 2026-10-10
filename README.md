# Conversational Predictive Maintenance and Decision Support System

**An Explainable AI and RAG-Based Platform for Failure Prediction, Remaining Useful Life Estimation, and Intelligent Maintenance Assistance**

## 📌 About the Project

The Conversational Predictive Maintenance and Decision Support System is a research-oriented software platform designed to analyse machine sensor data, predict potential equipment degradation, estimate Remaining Useful Life (RUL), and support maintenance decisions through explainable AI and conversational assistance.

The project integrates machine learning, uncertainty estimation, explainability, information retrieval, and large language models into a unified application. It aims to help users understand machine-health predictions, identify influential sensor readings, and access relevant maintenance knowledge through natural-language interaction.

NASA's Commercial Modular Aero-Propulsion System Simulation (C-MAPSS) dataset serves as the initial case study for developing and evaluating the predictive-maintenance pipeline.

## 🎯 Problem Statement

Traditional maintenance approaches often rely on reactive repairs or predefined maintenance schedules. These approaches may lead to unexpected downtime, unnecessary maintenance, increased operational costs, and difficulty identifying early signs of equipment degradation.

Although sensor data can provide useful information about machine health, converting that data into reliable, explainable, and actionable maintenance insights remains challenging.

This project explores how predictive modelling, explainable AI, uncertainty estimation, and retrieval-augmented conversational assistance can be integrated into a software platform to support informed maintenance decisions.

## 💡 Proposed Solution

The proposed system processes historical machine sensor data to estimate Remaining Useful Life and assess maintenance risk. It explains model predictions using SHAP and uses a retrieval-augmented generation (RAG) pipeline to provide context-grounded maintenance guidance through a conversational interface.

A web-based dashboard and backend API are planned to bring machine-health summaries, predictions, explanations, alerts, and conversational assistance into one application.

## ✨ Key Features

* **Remaining Useful Life Prediction:** Uses an XGBoost-based machine learning model to estimate the number of operating cycles remaining before the end of useful life.
* **Predictive Risk Assessment:** Estimates the risk of reaching a configurable RUL threshold and presents risk levels to support maintenance prioritisation.
* **Uncertainty Estimation:** Uses conformal prediction to provide uncertainty intervals around RUL estimates.
* **Explainable AI:** Applies SHAP to identify influential sensor features and explain their contributions to model predictions.
* **Conversational Maintenance Assistant:** Enables users to ask questions about machine health and maintenance information in natural language.
* **Retrieval-Augmented Generation (RAG):** Retrieves relevant technical knowledge to ground assistant responses in available documentation.
* **Maintenance Decision Support:** Combines model outputs, risk rules, explanations, and retrieved knowledge to support maintenance investigation and planning.
* **Machine Health Dashboard:** Plans to present machine status, RUL estimates, risk levels, historical trends, explanations, and alerts through a web interface.
* **Backend API and Database:** Uses FastAPI and PostgreSQL to support application functionality and persist machine, prediction, risk, alert, and conversation records.
* **Containerized Development:** Uses Docker Compose to support a consistent development environment.

## 🏗️ System Workflow

1. Load and validate historical machine sensor data.
2. Perform preprocessing and feature engineering.
3. Train and evaluate the XGBoost RUL prediction model.
4. Generate RUL estimates and uncertainty intervals.
5. Estimate risk against a configurable RUL threshold.
6. Explain predictions using SHAP.
7. Construct a machine-health summary.
8. Retrieve relevant maintenance knowledge using RAG.
9. Generate context-grounded conversational responses.
10. Present the results through the application dashboard and API.

## 🛠️ Technology Stack

| Component              | Technology                           |
| ---------------------- | ------------------------------------ |
| Programming Language   | Python                               |
| Predictive Modelling   | XGBoost                              |
| Explainability         | SHAP                                 |
| Uncertainty Estimation | Conformal Prediction                 |
| Backend API            | FastAPI                              |
| Database               | PostgreSQL                           |
| Frontend               | React                                |
| Conversational AI      | Large Language Model (LLM)           |
| Knowledge Retrieval    | Retrieval-Augmented Generation (RAG) |
| Containerization       | Docker and Docker Compose            |
| Version Control        | Git and GitHub                       |
| Experiment Tracking    | MLflow (planned)                     |

## 📊 Dataset

The initial research case study uses NASA's C-MAPSS turbofan engine degradation dataset, which contains simulated engine run-to-failure trajectories, operating settings, and sensor measurements collected over operating cycles.

Development begins with the FD001 subset, with additional subsets considered for further evaluation. Model evaluation is designed to use engine-level data splits to reduce data leakage between training and testing.

**Dataset source:** [NASA Prognostics Center of Excellence Data Repository](https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository/)

## 🔬 Explainability and Reliability

The project incorporates multiple methods to make predictive outputs more interpretable and evaluate their reliability:

* **SHAP:** Explains the influence of input features on individual predictions.
* **Conformal Prediction:** Produces RUL uncertainty intervals whose coverage can be evaluated on held-out engines.
* **Risk Calibration:** Evaluates estimated RUL-threshold probabilities using appropriate calibration metrics, including Brier score and reliability curves.
* **Model Evaluation:** Uses MAE, RMSE, R², and an asymmetric NASA-style scoring metric where appropriate.

Risk probabilities represent model-derived estimates of the probability that RUL is at or below a specified number of cycles. They are not guaranteed or ground-truth failure probabilities.

## ⚙️ Scope and Limitations

* The initial implementation focuses on historical and simulated C-MAPSS data.
* Live industrial telemetry and real-time sensor streaming are not part of the initial implementation.
* The platform is intended for research and maintenance decision support, not autonomous machine control.
* Results on simulated turbofan data do not establish performance on real industrial equipment.
* Predictive performance, uncertainty coverage, and risk calibration must be evaluated experimentally.

## 🚀 Project Status

The project is being developed incrementally, beginning with its architecture, database schema, and local development environment. Predictive modelling, explainability, conversational assistance, frontend integration, testing, and deployment are planned development stages.

Features should be marked as completed only after they have been implemented and tested.

## 👥 Team

Developed by a five-member final-year B.Tech Computer Science and Engineering team.

## 🙏 Acknowledgements

* NASA Prognostics Center of Excellence for the C-MAPSS dataset.
* The developers and maintainers of the open-source tools and frameworks used in this project.
* Project guide and faculty members for their guidance and feedback.
