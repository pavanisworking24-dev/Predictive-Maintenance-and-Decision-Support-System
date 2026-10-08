# Branch Strategy & Pull Request Guidelines

**Project:** Conversational Predictive Maintenance and Decision Support System  
**Repository:** conversational-predictive-maintenance  
**Team Size:** 5 Members  
**Document Status:** M0 — Product Foundation

## 1. Purpose
This document defines the Git branching strategy, branch naming conventions, commit guidelines, Pull Request (PR) process, and review rules for the project.

The purpose is to ensure that:
* The main branch remains stable.
* Team members can work independently without interfering with each other.
* Every code/documentation change can be traced to a GitHub Issue.
* Changes are reviewed before being merged.
* GitHub Actions CI is executed before merging.
* The team follows one consistent Git workflow throughout the project.

## 2. Core Development Workflow
All project work should follow this workflow:

1. GitHub Issue
2. Create Branch
3. Implement Task
4. Commit Changes
5. Push Branch
6. Create Pull Request
7. GitHub Actions CI
8. Code / Documentation Review
9. Resolve Review Comments
10. Approval
11. Merge into `main`
12. Delete Branch

**Golden Rule:** One Issue → One Working Branch → One Pull Request  
A branch should normally be created for a specific task rather than for a team member.

## 3. Main Branch
The `main` branch is the stable integration branch of the project.

* The `main` branch should contain only changes that have been reviewed and are considered safe to integrate.

**Rules:**
* Do not directly push changes to `main`.
* Do not develop features directly on `main`.
* Every meaningful change should come through a Pull Request.
* CI checks should pass before merging.
* Review comments must be resolved before merging.
* Keep `main` in a buildable and usable state.

**Example:**
* ❌ **Avoid:** `main` → Member 1 directly pushes code
* ✅ **Recommended:** `feature/fd001-data-exploration` → Pull Request → Review → CI → `main`

## 4. Working Branches
Team members should create temporary working branches from the latest `main` branch. The branch should represent the task or change, not the person working on it.

### Recommended Branch Categories

| Prefix | Purpose | Example |
| :--- | :--- | :--- |
| `feature/` | New functionality | `feature/fd001-data-loader` |
| `fix/` | Bug fixes | `fix/rul-calculation` |
| `docs/` | Documentation | `docs/literature-review` |
| `research/` | Research/experimental work | `research/conformal-prediction` |
| `test/` | Test-related work | `test/backend-api-tests` |
| `refactor/` | Code restructuring | `refactor/ml-pipeline` |
| `ci/` | CI/CD configuration | `ci/github-actions` |
| `chore/` | Maintenance/configuration | `chore/update-dependencies` |

## 5. Branch Naming Convention

**Format:** `<prefix>/<short-descriptive-name>`

**Examples:**
* **Feature:** `feature/fd001-data-exploration`, `feature/postgresql-schema`, `feature/fleet-dashboard`, `feature/rag-knowledge-base`, `feature/rul-prediction`
* **Documentation:** `docs/literature-review`, `docs/architecture-documentation`, `docs/branch-pr-guidelines`
* **Bug fixes:** `fix/rul-calculation`, `fix/api-validation`, `fix/database-migration`
* **CI:** `ci/github-actions`, `ci/backend-tests`
* **Research:** `research/conformal-prediction`, `research/shap-analysis`

**Branch Naming Rules:**
* Use lowercase.
* Use hyphens between words.
* Keep the name short but meaningful.
* Avoid spaces.
* Avoid personal names.
* Avoid vague names such as: `my-branch`, `test`, `new`, `changes`, `member1-work`

**Avoid:** `member3-final-work`  
**Recommended:** `feature/postgresql-schema`

## 6. Branch Creation
Before creating a branch, make sure your local `main` is up to date:

```bash
git checkout main
git pull origin main
```

Then create your working branch:

```bash
git checkout -b feature/postgresql-schema
```

Verify the branch:

```bash
git branch
```
*(The active branch will be marked with `*`)*

## 7. Working on a Task
After creating the branch, make the required changes.

**Example:**
* **Issue:** [M0][PLATFORM] Set Up PostgreSQL Schema v0
* **Branch:** `feature/postgresql-schema`

Work should remain limited to the scope of the issue whenever practical. Avoid mixing unrelated changes into the same branch. It should not contain unrelated frontend redesigns, for instance.

## 8. Commit Guidelines
Commits should clearly describe what changed.

**Format:** `<type>: <short description>`

### Commit Types
* `feat`: New functionality
* `fix`: Bug fix
* `docs`: Documentation
* `test`: Tests
* `ci`: CI/CD changes
* `refactor`: Code restructuring
* `chore`: Maintenance/configuration

**Examples:**
```bash
git commit -m "feat: add FD001 data loader"
git commit -m "docs: add branch and PR guidelines"
git commit -m "ci: add GitHub Actions workflow"
git commit -m "feat: add PostgreSQL schema v0"
git commit -m "test: add RUL calculation tests"
git commit -m "fix: correct RUL calculation"
```

**Commit Rules:**
* Keep commits focused.
* Write meaningful commit messages.
* Avoid messages such as: `changes`, `update`, `final`, `done`, `work`, `asdf`.
* Do not commit passwords, API keys, tokens, or `.env` files.
* Do not commit raw/private datasets that are excluded by the project `.gitignore`.

## 9. Push the Working Branch
After completing a meaningful portion of the task:

```bash
git status
git add .
git commit -m "feat: add PostgreSQL schema v0"
git push -u origin feature/postgresql-schema
```

For subsequent pushes to the same branch:

```bash
git push
```

## 10. Pull Request Guidelines
Once the task is ready for review, create a Pull Request from the working branch into `main`.
Do not create a PR directly into another member's feature branch unless the team explicitly requires it.

## 11. Pull Request Title
PR titles should be concise and clearly describe the change.

**Format:** `<type>: <description>`

**Examples:**
* `feat: add PostgreSQL schema v0`
* `docs: add branch and PR guidelines`
* `ci: add GitHub Actions CI skeleton`
* `feat: implement FD001 data loader`
* `fix: correct RUL calculation`

## 12. Pull Request Description
Every PR should explain what was changed and how it was verified.

**Use the following template:**
```markdown
## Summary
Briefly describe what this PR implements.

## Related Issue
Closes #<issue-number>

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing / Verification
- [ ] Tested locally
- [ ] GitHub Actions CI passes
- [ ] No existing functionality was broken

## Screenshots / Evidence
Add screenshots or other evidence if applicable.

## Review Notes
Mention anything the reviewer should pay special attention to.
```

## 13. Example Pull Request
**PR Title:** `feat: add PostgreSQL schema v0`

**Description:**
```markdown
## Summary
Adds the initial PostgreSQL database schema for the project.

## Related Issue
Closes #15

## Changes Made
- Added SQLAlchemy database models
- Added Users table
- Added Machines table
- Added Predictions table
- Added RiskScores table
- Added ModelVersions table
- Added initial relationships and constraints
- Added Alembic migration

## Testing / Verification
- [x] Tested locally
- [x] Migration runs successfully
- [x] GitHub Actions CI passes
- [x] No existing functionality was broken

## Screenshots / Evidence
Database migration output attached.

## Review Notes
Please review the relationships and naming conventions before merging.
```

## 14. Pull Request Review Process
Every meaningful PR should be reviewed by at least one other team member. The PR author should not approve their own PR.

**Review Process:**
1. Developer creates PR
2. CI runs
3. Reviewer checks changes
4. If changes needed → Author updates branch → Re-review
5. If approved → Merge

## 15. What Reviewers Should Check
* **Functionality:** Does the implementation satisfy the Issue? Does it behave as expected?
* **Code Quality:** Is the code understandable? Is the structure consistent with the project?
* **Project Architecture:** Does the change follow the agreed architecture? Does it conflict with another module?
* **Testing:** Are appropriate tests included? Does CI pass? Was the change tested locally?
* **Security:** Check for accidentally committed API keys, passwords, tokens, `.env` files, or private credentials.
* **Documentation:** Is the relevant documentation updated if APIs, architecture, or workflows changed?

## 16. Review Comments
Reviewers should provide clear and constructive feedback.

* **Good:** "The database schema currently allows duplicate (dataset_id, engine_id) combinations. Please consider adding a unique constraint so that each machine is uniquely identified."
* **Avoid:** "This is wrong." or "Change this."

## 17. Resolving Review Comments
If changes are requested:
1. Make the required changes on the same branch.
2. Commit the changes.
3. Push the branch again.
4. Ask the reviewer to re-check the changes (PR updates automatically).

```bash
git add .
git commit -m "fix: address database review comments"
git push
```
Do not create a completely new PR for every review comment.

## 18. GitHub Actions CI Requirement
The project uses GitHub Actions for CI. Before merging a PR, `CI → PASS` should normally be required.

## 19. Keep the PR Focused
A PR should normally represent one logical change.
* **Good PR:** `feat: add PostgreSQL schema v0` (Contains models, migrations, constraints, tests related to schema).
* **Poor PR:** `update project` (Contains schema, React dashboard, RAG pipeline, CI, README changes mixed together).

## 20. Avoid Direct Changes to main

**Avoid:**
```bash
git checkout main
# make changes
git add .
git commit
git push
```

**Instead:**
```bash
git checkout main  
git pull origin main  
git checkout -b feature/my-task
# work
git add .  
git commit -m "feat: implement my task"  
git push -u origin feature/my-task
```

## 21. Keeping Branches Updated
If `main` has changed while you are working on your feature:

```bash
git checkout main
git pull origin main
git checkout feature/my-task
git merge main
# Resolve conflicts if any
git push
```

## 22. Merge Conflicts
If a conflict occurs:
1. Do not panic or randomly delete changes.
2. Identify the conflicting files.
3. Keep the correct combined version.
4. Test the result.
5. Commit the resolution.
6. Push the branch.
7. Re-run CI.

## 23. Merging the Pull Request
A PR should be merged only after:
* The Issue requirements are satisfied.
* CI passes.
* Required review is completed and comments are resolved.
* After merging, **delete the remote feature branch**.

## 24. Issue → Branch → PR Mapping
Every development task should have a traceable relationship:  
`GitHub Issue` → `Git Branch` → `Pull Request` → `Commit(s)` → `main`

## 25. Recommended Workflow for This Project
* **Member 1 (Data / ML):** Issue → `feature/fd001-data-exploration` → PR → Review → `main`
* **Member 2 (Reliability / Explainability):** Issue → `feature/risk-engine` → PR → Review → `main`
* **Member 3 (Backend / Database):** Issue → `feature/postgresql-schema` → PR → Review → `main`
* **Member 4 (Frontend):** Issue → `feature/fleet-dashboard` → PR → Review → `main`
* **Member 5 (RAG / LLM):** Issue → `feature/rag-knowledge-base` → PR → Review → `main`

## 26. M0 Branch Strategy
During M0, establish the workflow using small tasks like `ci/github-actions`, `docs/branch-pr-guidelines`, `feature/postgresql-schema`. Link each to a GitHub Issue.

## 27. Quick Reference
* **Start a task:** `git checkout main`, `git pull origin main`, `git checkout -b feature/task-name`
* **Stage & Commit:** `git add .`, `git commit -m "feat: describe the change"`
* **Push:** `git push -u origin feature/task-name` (first time) or `git push` (subsequent)

## 28. Team Rules — Final Checklist
Before considering a task complete:
- [ ] A GitHub Issue exists.
- [ ] A task-specific branch was created.
- [ ] Branch name follows the naming convention.
- [ ] Changes are limited to the task scope.
- [ ] Commit messages are meaningful.
- [ ] No secrets or unnecessary files are committed.
- [ ] Pull Request is linked to the Issue.
- [ ] CI passes.
- [ ] At least one team member reviews the PR.
- [ ] PR is merged into `main` and branch is deleted.

## 29. Final Team Principle
`main` is the stable branch. Issues define the work. Branches isolate the work. Pull Requests review the work. CI validates the work. Reviews protect the quality.