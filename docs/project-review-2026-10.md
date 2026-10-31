# Project Review: Validation of External Review Findings (21 October 2026)

An external review listed 25 problems. Each was checked against the repository, the scope document and the generated outputs. **Verdict** says whether the finding is correct; **Status** says what was done.

Status values: **Done** (file changed in this batch), **Needs team** (a decision or sign-off is required), **Next** (not done yet).

## 1. Project scope

| # | Finding | Verdict | Evidence and fix | Status |
|---|---|---|---|---|
| 1 | The 85–95% coverage criterion is too tight for 100 test engines | **Partly valid.** The direction is right, the size is overstated | Exact binomial calculation, assuming a method whose true coverage is exactly 90%: it falls outside 85–95% in **6.4%** of runs with 100 engines (FD001, FD003), in 0.8% with about 250 engines (FD002, FD004), and in **13.7%** of runs for at least one of the four subsets. About ±6.0 points would be needed for a 95% pass rate at n = 100. The real failure rate is higher because the calibration set adds its own variance. Fix: report observed coverage with an exact 95% confidence interval and accept the result when 90% lies inside it (scope 3.12 and 9.6) | Done |
| 2 | Held-out calibration engines reduce training data, so results are not comparable with published numbers | **Valid** | Calibration now uses out-of-fold residuals (engine-level 5-fold, cross-conformal / CV+ style) and Experiment A trains on all training engines (scope 3.3, 3.7, 3.8, M3). The theoretical guarantee of this variant is weaker than split conformal, so coverage is validated empirically on the test engines (stated in the scope) | Done |
| 3 | Experiment B does not say how regimes and features are handled | **Valid** | Scope 3.7 now defines B1 (FD001 pipeline unchanged) and B2 (FD001 model with regime normalization fitted on the target's training sensors, no labels), a fixed FD001 feature list, the same cap and last-cycle protocol, and unchanged FD001 conformal intervals so that the loss of coverage is measured | Done |
| 4 | Admin powers, the fleet report and monitoring have no endpoints or tables | **Valid** | OpenAPI now has 30 operations: users, risk thresholds, model versions and activation, knowledge-base documents, `GET /reports/fleet`, `GET /metrics`. New table `risk_threshold_configs` (versioned, one active, referenced by `risk_scores`) and `knowledge_documents.ingestion_status`. Contract tests check roles and database parity. The backend that implements them is still to be written | Done (contract and schema) |
| 5 | Risk-band rule table and alert logic are not defined | **Valid** | `docs/architecture/risk-and-alert-rules-v0.md`: band rule, default configuration `cfg-1`, evaluation labels, alert types, de-duplication, lifecycle, test cases, and the first decision rules. Values are proposals | Done, **Needs team** (sign-off) |
| 6 | Embedding model not chosen (schema fixed at 384 dimensions) | **Valid** | `docs/architecture/rag-decisions-v0.md`: proposed default all-MiniLM-L6-v2, comparison with bge-small-en-v1.5 on the gold set, both 384-dimensional so the schema stays. The final choice depends on retrieval results | Proposed, **Needs team** |
| 7 | `POST /predictions` has no role rule | **Valid** (low) | Rule added to the permission matrix: all roles, rate-limited per user | Done |

## 2. Notebook (FD001 exploratory analysis)

| # | Finding | Verdict | Evidence and fix | Status |
|---|---|---|---|---|
| 8 | Works only in Colab and loads data from the working directory | **Valid** | `notebooks/cmapss_eda.ipynb` reads `data/raw/` (or `CMAPSS_DATA_DIR`), unzips a downloaded archive portably, and has no Colab calls | Done |
| 9 | Unzip runs after the data load | **Valid** (low) | Extraction is now the first step of the loading cell | Done |
| 10 | Low-variance detection uses raw standard deviation | **Valid, and the effect is worse than stated.** The old table shows one distinct value for sensors 1, 5, 10 and 16, yet they were reported as "low variance" because of a tiny floating-point standard deviation | Constants are found by counting distinct values (per regime). Low resolution is a separate flag. Signal strength is the scale-free Spearman correlation with capped RUL after regime normalization | Done |
| 11 | Only FD001 is analysed | **Valid** | The notebook loops over FD001–FD004, recovers the six regimes for FD002 and FD004, and skips subsets whose files are missing | Done in code; **Next:** run it on the real data |
| 12 | Figures save to the working directory | **Valid** (low) | Figures go to `docs/dataset/figures/<subset>_*.png`; tables to `docs/dataset/` | Done |

## 3. Documents and contracts

| # | Finding | Verdict | Evidence and fix | Status |
|---|---|---|---|---|
| 13 | The Health Summary example is inconsistent (RUL 18, interval 14–23, P(RUL ≤ 30) = 0.81) | **Valid** | The interval's upper bound (23) is below 30, so at 90% coverage P(RUL ≤ 30) must be at least 0.90. Example changed to 0.98; a rule and three tests now catch this kind of contradiction | Done |
| 14 | No SRS although M0 requires one | **Valid** | Not written in this batch | **Next** |
| 15 | No mock API serving mock data although M0 requires it | **Valid** | Only one example payload exists. Not built in this batch | **Next** |
| 16 | Citations: unverified DOIs, weak sources, one mismatch | **Valid** | Entries 5, 9, 11, 12, 14, 15 and 20 now carry confirmed identifiers. Two author lists were wrong: entry 9 (Lewis, Perez, Piktus et al., not Guu and Lomeli) and entry 11 (Logan Cummins and Alexander Sommers). The untraceable "[Scientific Reports, 2025]" in the research-gap analysis is replaced by Balasubramani et al. (2024), the source the literature review uses for the same statement. Still open: entries 13, 16 (weak venue) and 17; entries 1–4, 6–8 and 10 were not re-checked | Mostly done, **Needs team** |

## 4. Repository and code

| # | Finding | Verdict | Evidence and fix | Status |
|---|---|---|---|---|
| 17 | `ml/`, `backend/`, `frontend/`, `rag/` hold only placeholders; M1 has not started | **Valid** | Placeholders are now short READMEs that state the purpose and milestone. The M1 pipeline itself is not written | **Next** (critical path) |
| 18 | LICENSE is empty | **Valid** (low) | The file had 0 bytes. An MIT draft is included; the team and the college must confirm the license | Done, **Needs team** |
| 19 | `backend/frontend.txt` is misnamed | **Valid** (low) | Removed; replaced by `backend/README.md` | Done |
| 20 | CI lints only `tests/` | **Valid** (low) | `ruff check .` with `ruff.toml` (notebooks excluded until outputs are stripped) | Done |
| 21 | Demo seed is mounted in Compose | **Valid** | The seed moved to `docker-compose.override.yml`, which Compose loads only for local development. Deployments run `docker compose -f docker-compose.yml up` | Done |

## 5. Team and process

| # | Finding | Verdict | Evidence and suggestion | Status |
|---|---|---|---|---|
| 22 | Member 3 carries the heaviest workload | **Plausible** | By the ownership table, Member 3 owns the database, backend, authentication, Docker, CI/CD, cloud and logging, and is backup for Members 4 and 5. Member 1 also owns three milestones plus the four-subset experiments. Suggest the team moves deployment preparation (M14) or the CI upkeep to another member | **Needs team** |
| 23 | One account made 26 of 30 non-merge commits | **Valid** | The repository snapshot reviewed here shows 25 of 29 (86%). One teammate appears under two identities. Suggest each member opens their own pull requests and adds a `.mailmap` so identities merge | **Needs team** |
| 24 | The 31 October go/no-go is 11 days away, with exams in November | **Valid** (10 days from 21 October) | The scope's own rule applies: unfinished M1 work moves to the December sprint and no catch-up is done during exams. See section 6 | **Needs team** |

## 6. Proposed plan for 21–31 October (for the team to adjust)

Target: the FD001 path only. FD002–FD004 wait.

| By | Who | Deliverable |
|---|---|---|
| 24 Oct | Member 1 | FD001 loader, RUL construction with the 125 cap, engine-level splits (M1 start) |
| 26 Oct | Member 1 | Causal rolling features and the validation checks (schema, nulls, duplicates, continuity, leakage, contamination) with tests |
| 28 Oct | Member 1 | Linear Regression, Random Forest and XGBoost baselines on FD001 with the last-cycle protocol (M2 start) |
| 28 Oct | Members 2 and 5 | Review and sign-off of the risk thresholds and the decision rules; start the sensor → component table |
| 29 Oct | Member 3 | Merge the pending pull requests; real FD001 data loaded into the database |
| 30 Oct | Member 4 | Wireframes connected to the mock Health Summary data |
| 31 Oct | All | Go/no-go: if the FD001 pipeline and baselines are not finished, record it and carry the work into the December sprint |

## 7. What was not verified

- The notebook was tested on synthetic C-MAPSS-shaped data only; it has not run on the real files.
- The SQL changes were not executed on a PostgreSQL server here. The CI job `Docker Compose and Database` and `scripts/check_db.sh` test them.
- Four contract tests need the `jsonschema` library and have to be run on your machine or in CI.
- Citation identifiers were checked through publisher and index pages, not through the publishers' own full text.