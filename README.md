# Conversational Predictive Maintenance and Decision Support System

**An Explainable AI and RAG-Based Platform for Failure Prediction, Remaining Useful Life Estimation, and Intelligent Maintenance Assistance**

[![CI](https://github.com/pavanisworking24-dev/Predictive-Maintenance-and-Decision-Support-System/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pavanisworking24-dev/Predictive-Maintenance-and-Decision-Support-System/actions/workflows/ci.yml)

> **Disclaimer:** This is research-oriented decision support based on simulated C-MAPSS data and retrieved technical knowledge. It is not certified maintenance advice and must not be used for real maintenance or flight-safety decisions.

## 📌 About the Project

The Conversational Predictive Maintenance and Decision Support System is a research-oriented software platform designed to analyse machine sensor data, predict potential equipment degradation, estimate Remaining Useful Life (RUL), and support maintenance decisions through explainable AI and conversational assistance.

The project integrates machine learning, uncertainty estimation, explainability, information retrieval, and large language models into a unified application. It aims to help users understand machine-health predictions, identify influential sensor readings, and access relevant technical knowledge through natural-language interaction.

NASA's Commercial Modular Aero-Propulsion System Simulation (C-MAPSS) dataset serves as the case study for developing and evaluating the predictive-maintenance pipeline.

## 🎯 Problem Statement

Traditional maintenance approaches often rely on reactive repairs or predefined maintenance schedules. These approaches may lead to unexpected downtime, unnecessary maintenance, increased operational costs, and difficulty identifying early signs of equipment degradation.

Although sensor data can provide useful information about machine health, converting that data into reliable, explainable, and actionable maintenance insights remains challenging.

This project explores how predictive modelling, explainable AI, uncertainty estimation, and retrieval-augmented conversational assistance can be integrated into a software platform to support informed maintenance decisions.

## 💡 Proposed Solution

The system processes historical machine sensor data to estimate Remaining Useful Life and assess maintenance risk. It explains model predictions using SHAP and uses a retrieval-augmented generation (RAG) pipeline to provide context-grounded guidance through a conversational interface.

A web dashboard and backend API bring machine-health summaries, predictions, explanations, alerts, and conversational assistance into one application. The current data flow is **C-MAPSS → batch processing → prediction → database → dashboard**. It is not a live telemetry pipeline.

## ✨ Planned Features

The features below describe the target design. See [Project Status](#-project-status) for what is implemented today.

* **Remaining Useful Life Prediction:** Linear Regression and Random Forest baselines and an XGBoost primary model, one per C-MAPSS subset.
* **Predictive Risk Assessment:** Estimates the probability that RUL is at or below a configurable threshold and assigns LOW, MEDIUM, or HIGH risk.
* **Uncertainty Estimation:** Split conformal prediction intervals calibrated on held-out engines.
* **Explainable AI:** SHAP explanations, local and global, aggregated to sensor level for display.
* **Machine Health Summary:** One versioned object that combines RUL, interval, risk, explanation, and recommendation. The frontend, backend, and assistant all build on it.
* **Decision Support:** An explicit, documented rule table that turns risk level, top contributing sensors, and uncertainty into investigation guidance.
* **Conversational Assistant and RAG:** Grounded answers with source references, using retrieved knowledge and the machine's health summary, behind a provider-independent LLM interface.
* **Alerts:** Created automatically when risk changes to HIGH, and acknowledged or assigned by authorised users.
* **Web Application:** React dashboard, FastAPI backend, and PostgreSQL database with JWT authentication and three roles (Admin, Maintenance Manager, Maintenance Engineer).
* **Engineering:** Docker Compose, GitHub Actions CI, MLflow tracking with a manual model registry, and deployment to AWS on a single virtual machine.

## 🏗️ System Workflow

1. Load and validate historical C-MAPSS sensor data through one generic loader.
2. Perform causal preprocessing and feature engineering (trailing windows only, no future information).
3. Train and evaluate the RUL models with engine-level splits.
4. Generate RUL estimates and conformal uncertainty intervals.
5. Estimate risk against a configurable RUL threshold.
6. Explain predictions using SHAP.
7. Build the Machine Health Summary and store it in PostgreSQL.
8. Retrieve relevant knowledge using RAG (pgvector).
9. Generate context-grounded conversational responses.
10. Present results through the dashboard and API.

## 🛠️ Technology Stack

| Component              | Technology                               | Status                    |
| ---------------------- | ---------------------------------------- | ------------------------- |
| Programming Language   | Python                                   | In use                    |
| Database               | PostgreSQL 16 with pgvector              | In use (local Compose)    |
| API Contract           | OpenAPI 3.0 and JSON Schema              | In use                    |
| Containerization       | Docker and Docker Compose                | In use (database only)    |
| CI                     | GitHub Actions, pytest, ruff             | In use                    |
| Version Control        | Git and GitHub                           | In use                    |
| Predictive Modelling   | Linear Regression, Random Forest, XGBoost | Planned                  |
| Explainability         | SHAP                                     | Planned                   |
| Uncertainty Estimation | Conformal Prediction                     | Planned                   |
| Backend API            | FastAPI                                  | Planned                   |
| Frontend               | React                                    | Planned                   |
| Conversational AI      | Hosted LLM behind a provider-independent interface | Planned         |
| Knowledge Retrieval    | RAG with pgvector                        | Planned (schema ready)    |
| Experiment Tracking    | MLflow                                   | Planned                   |
| Deployment             | AWS, single VM with Docker Compose       | Planned                   |

## 📊 Dataset

The case study uses NASA's C-MAPSS turbofan engine degradation dataset, which contains simulated engine run-to-failure trajectories, operating settings, and sensor measurements collected over operating cycles. All four subsets are in scope:

| Subset | Operating conditions | Fault modes | Role |
| ------ | -------------------- | ----------- | ---- |
| FD001  | 1                    | 1           | Development and primary demonstration |
| FD003  | 1                    | 2           | Fault-mode robustness |
| FD002  | 6                    | 1           | Operating-condition robustness |
| FD004  | 6                    | 2           | Combined and most challenging case |

Development starts with FD001 and a vertical slice before the other subsets are added. Evaluation uses engine-level splits (a whole engine stays in one partition), a 125-cycle cap on training RUL labels, and the official uncapped test RUL at each engine's last cycle as the primary protocol.

The raw data files are not stored in this repository. Download them from the source below and keep them outside version control (the `.gitignore` excludes them).

**Dataset source:** [NASA Prognostics Center of Excellence Data Repository](https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository/)

## 🔬 Explainability and Reliability

* **SHAP:** Explains the influence of input features on individual predictions.
* **Conformal Prediction:** Produces RUL uncertainty intervals whose coverage is evaluated on held-out engines. The target is 90% nominal coverage, accepted within 85–95% overall.
* **Risk Calibration:** Evaluates estimated RUL-threshold probabilities with reliability curves and the Brier score before they are displayed.
* **Model Evaluation:** MAE, RMSE, R², and the asymmetric PHM08 score, with engine-level, early-life, and late-life error analysis.

Risk probabilities are model-derived estimates of the probability that RUL is at or below a specified number of cycles. They are not guaranteed or ground-truth failure probabilities.

## 🚀 Quick Start

Currently the runnable part of the project is the local PostgreSQL database and the contract checks.

**Prerequisites:** Docker Desktop (running), Git, and Python 3.12 or newer. On Windows, run the shell commands in Git Bash.

```bash
# 1. Clone the repository
git clone https://github.com/pavanisworking24-dev/Predictive-Maintenance-and-Decision-Support-System.git
cd Predictive-Maintenance-and-Decision-Support-System

# 2. Create your local environment file (never commit .env)
cp .env.example .env

# 3. Start PostgreSQL with pgvector; the schema and a development seed load on first start
docker compose up -d --wait

# 4. Verify the database (14 tables, pgvector, seed data, constraints)
bash scripts/check_db.sh
```

**Database connection (defaults):**

| Setting  | Value                                    |
| -------- | ---------------------------------------- |
| Host     | `localhost`                              |
| Port     | `5433` (`POSTGRES_HOST_PORT` in `.env`)  |
| Database | `predictive_maintenance`                 |
| User     | `pm_user`                                |
| Password | the `POSTGRES_PASSWORD` value in `.env`  |

The schema and seed scripts run only when the data volume is empty. To rebuild the database from scratch (this deletes local data):

```bash
docker compose down -v
docker compose up -d --wait
```

**Run the contract tests and lint locally:**

```bash
pip install pytest PyYAML jsonschema openapi-spec-validator ruff
python -m pytest tests/contracts -q
openapi-spec-validator docs/api/openapi.yaml
ruff check .
```

More detail, including troubleshooting, is in the [database setup guide](docs/database/database-setup-documentation.md).

## 🔌 API Contract

The REST API is defined in [`docs/api/openapi.yaml`](docs/api/openapi.yaml) before it is implemented, so the frontend, backend, and assistant can be built in parallel. It covers authentication, machines, sensor readings, predictions, health summaries, risk, explanations, maintenance records, alerts, and the assistant, with JWT bearer authentication and role-restricted operations. The Machine Health Summary is defined in [`docs/contracts/health-summary-v0.schema.json`](docs/contracts/health-summary-v0.schema.json).

The FastAPI backend that serves this contract is not implemented yet. Machines are identified by a readable code such as `FD001-E047`.

## ✅ Continuous Integration

GitHub Actions runs on every pull request to `main` and on pushes to `main`:

* **Project Structure and Contract Validation:** checks the required files, validates the OpenAPI document, the Health Summary JSON Schema and its example, and runs the contract tests. These tests also check that OpenAPI and the database schema agree.
* **Python Lint:** runs `ruff`.
* **Docker Compose and Database:** validates the Compose file, starts PostgreSQL with pgvector on a clean machine, and runs `scripts/check_db.sh`.

## 📁 Repository Structure

```text
.
├── .github/workflows/ci.yml      # CI pipeline
├── backend/                      # FastAPI backend (planned)
├── docker/                       # Container files (planned)
├── docs/
│   ├── api/                      # OpenAPI contract
│   ├── architecture/             # System architecture and integration notes
│   ├── contracts/                # Machine Health Summary schema and example
│   ├── database/                 # SQL schema, seed data, setup guide
│   ├── dataset/                  # C-MAPSS exploratory analysis tables and figures
│   ├── Knowledge/                # Knowledge-source inventory
│   └── M0 - Literature Review and Research Gap/
├── frontend/                     # React application (planned)
├── ml/                           # Data pipeline and models (planned)
├── notebooks/                    # C-MAPSS exploratory analysis (FD001–FD004)
├── rag/                          # Knowledge base and retrieval (planned)
├── scripts/check_db.sh           # Database verification
├── tests/contracts/              # Contract tests
├── docker-compose.yml            # Local PostgreSQL with pgvector
├── docker-compose.override.yml   # Development seed data (never deployed)
└── .env.example                  # Environment variable template
```

## 📚 Documentation

| Document | Description |
| -------- | ----------- |
| [System architecture](docs/architecture/system-architecture-v0.md) | Components, boundaries, and decisions |
| [Integration notes](docs/architecture/integration-notes-v0.md) | How the API, database, and Health Summary fit together |
| [OpenAPI contract](docs/api/openapi.yaml) | Planned REST API |
| [Health Summary schema](docs/contracts/health-summary-v0.schema.json) and [example](docs/contracts/health-summary-v0.example.json) | The integration contract |
| [Database setup guide](docs/database/database-setup-documentation.md) | Schema, tables, setup, and troubleshooting |
| [Software requirements specification](docs/srs/software-requirements-specification-v0.md) | Requirements with ids, tiers and milestone traceability |
| [Risk and alert rules](docs/architecture/risk-and-alert-rules-v0.md) | Risk bands, alert logic and decision rules (proposed) |
| [RAG decisions](docs/architecture/rag-decisions-v0.md) | Embedding model choice and comparison plan |
| [Project review](docs/project-review-2026-10.md) | Validation of the external review findings |
| [FD001 exploration findings](docs/dataset/fd001-eda-findings.md) | Dataset analysis |
| [Literature review](docs/M0%20-%20Literature%20Review%20and%20Research%20Gap/literature-review.md) and [research gap analysis](docs/M0%20-%20Literature%20Review%20and%20Research%20Gap/research-gap-analysis.md) | Background and motivation |
| [Knowledge-source inventory](docs/Knowledge/knowledge-source-inventory-v0.md) | Sources for the RAG knowledge base |
| [Branch strategy and pull request guidelines](docs/branch_strategy_pull_request_guidelines.md) | How the team works in Git |

## ⚙️ Scope and Limitations

* All sensor data is simulated. Results on C-MAPSS do not establish performance on real industrial equipment.
* The project does not use real aircraft telemetry, real-time monitoring, or a production fleet, and it does not provide certified maintenance advice.
* Users, maintenance records, alerts, and chat records are generated by the application. Maintenance recommendations are rule-based decision support and do not reflect engineering practice.
* The knowledge base covers the simulator and prognostics literature, not real maintenance manuals.
* Predictions near the 125-cycle cap carry limited information and are displayed as "≥ 125".
* Predictive performance, uncertainty coverage, and risk calibration must be evaluated experimentally; no accuracy target is promised in advance.

## 🚧 Project Status

The project is developed incrementally. A feature is marked as done only after it is implemented and tested.

| Area | Status |
| ---- | ------ |
| Scope, architecture, and literature review | Done |
| FD001 exploratory data analysis | Done |
| Health Summary schema and example | Done, validated in CI |
| OpenAPI contract | Done, validated in CI |
| Database schema, seed data, and local setup | Done, verified in CI |
| Contract tests, lint, and CI | Done |
| Data pipeline and validation suite | Next |
| RUL models, uncertainty, risk, SHAP | Planned |
| Backend (FastAPI) and authentication | Planned |
| Knowledge base, RAG, and assistant | Planned |
| Frontend (React) | Planned |
| MLflow, AWS deployment, monitoring | Planned |

The first milestone after the foundation is a vertical slice: FD001 → XGBoost → database → API → one dashboard page → chat stub, running in Docker Compose.

## 🤝 Contributing

Work follows one issue, one branch, one pull request, with CI passing before merge into `main`. See the [branch strategy and pull request guidelines](docs/branch_strategy_pull_request_guidelines.md). Never commit `.env` files, credentials, raw datasets, or model artifacts.

## 👥 Team

Developed by a five-member final-year B.Tech Computer Science and Engineering team.

## 📄 License

See the [LICENSE](LICENSE) file.

## 🙏 Acknowledgements

* NASA Prognostics Center of Excellence for the C-MAPSS dataset.
* A. Saxena and K. Goebel (2008), "Turbofan Engine Degradation Simulation Data Set", and A. Saxena, K. Goebel, D. Simon, and N. Eklund (2008), "Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation", PHM08.
* The developers and maintainers of the open-source tools and frameworks used in this project.
* Project guide and faculty members for their guidance and feedback.