# Database Setup Documentation — Predictive Maintenance and Decision-Support System

## 1. Purpose

This document describes the PostgreSQL database used by the **Predictive Maintenance and Decision-Support System**. It covers local setup, the schema, tables, primary and foreign keys, relationships, constraints, indexes, seed data, verification queries, and common troubleshooting steps.

The database is intended to store machine metadata, sensor readings, model versions, RUL predictions, risk scores, alerts, maintenance records, chat history, and knowledge-document metadata.

> **Scope note:** This document describes the database schema and local development setup. It does not implement prediction logic, an API, a dashboard, authentication flows, or an LLM/RAG pipeline.

## 2. Database technology and local configuration

The project uses **PostgreSQL 16**, commonly run locally through Docker Compose.

The previously used development configuration is:

| Setting | Value |
|---|---|
| Database | `predictive_maintenance` |
| Database user | `pm_user` |
| PostgreSQL port | `5432` |
| Database container name seen in prior setup | `predictive-maintenance-postgres` |
| Schema file | `docs/database/database-schema-v0.sql` |
| Seed file | `docs/database/seed-v0.sql` |

The development password was previously set to `pm_password`, but **check the current Compose or environment configuration before using it**. Do not commit real credentials or production secrets to Git.

## 3. Repository files

Expected database-related files:

```text
docs/
└── database/
    ├── database-schema-v0.sql
    └── seed-v0.sql
```

- `database-schema-v0.sql` creates the database tables, constraints, and indexes.
- `seed-v0.sql` inserts a small set of development/sample records.

The database itself is created by PostgreSQL or Docker Compose configuration. A SQL schema file normally creates tables inside an already selected database; it does not necessarily create the database or database user.

## 4. Start PostgreSQL with Docker Compose

Run commands from the project root—the folder containing the Compose file.

### 4.1 Start the database

In Windows Command Prompt (CMD):

```bat
docker compose up -d
docker compose ps
```

Confirm that the PostgreSQL service is running and healthy.

If the Compose service is named `postgres`, you can inspect its logs with:

```bat
docker compose logs postgres
```

If your service has a different name, use the service name shown by `docker compose ps`.

### 4.2 Confirm the container

```bat
docker ps
```

Look for the PostgreSQL container and its published port. If PostgreSQL is not running, inspect the Compose logs before continuing.

## 5. Apply the schema

Choose the command that matches your Compose configuration.

### Option A — Use the running Compose service

If the service is named `postgres` and the SQL files are available in the project directory, one common method is to copy the files into the container and run `psql`:

```bat
docker cp docs\database\database-schema-v0.sql predictive-maintenance-postgres:/tmp/database-schema-v0.sql
docker exec -it predictive-maintenance-postgres psql -U pm_user -d predictive_maintenance -f /tmp/database-schema-v0.sql
```

If the actual container name differs, replace `predictive-maintenance-postgres` with the name returned by `docker ps`.

### Option B — Run `psql` inside the container

If the SQL files are mounted into the container by Compose, use their actual in-container paths:

```bat
docker compose exec postgres psql -U pm_user -d predictive_maintenance
```

Then, at the `psql` prompt, use `\i` with the path visible **inside the container**. A Windows path such as `C:\Users\...` is not automatically accessible inside the container.

### Option C — Use pgAdmin

1. Open pgAdmin and connect to the PostgreSQL server.
2. Select the `predictive_maintenance` database.
3. Open **Tools → Query Tool**.
4. Open or paste the contents of `docs/database/database-schema-v0.sql`.
5. Execute the script.
6. Refresh **Schemas → public → Tables**.

Use one schema-application method, not all methods repeatedly. If the schema has already been applied, inspect the existing tables first. Some SQL scripts are not designed to be run multiple times.

## 6. Apply seed data

After the schema is successfully created, apply the seed file once.

For example, using the container-copy method:

```bat
docker cp docs\database\seed-v0.sql predictive-maintenance-postgres:/tmp/seed-v0.sql
docker exec -it predictive-maintenance-postgres psql -U pm_user -d predictive_maintenance -f /tmp/seed-v0.sql
```

Or execute `seed-v0.sql` in pgAdmin's Query Tool while connected to `predictive_maintenance`.

Seed data is for development and verification only. Review the seed script before re-running it to check whether it inserts duplicate records or assumes an empty database.

## 7. Database schema overview

The schema contains **11 tables**:

| Table | Purpose |
|---|---|
| `users` | Stores application user records and role information. |
| `machines` | Stores machine/engine identity and dataset identifiers. |
| `sensor_readings` | Stores sensor and operating-setting values by machine cycle. |
| `model_versions` | Records model metadata and artifact/version information. |
| `predictions` | Stores predicted RUL values and optional uncertainty bounds. |
| `risk_scores` | Stores risk level and threshold/probability information associated with predictions. |
| `alerts` | Stores machine alerts, severity, status, acknowledgement, and assignment. |
| `maintenance_records` | Stores maintenance work records and their status. |
| `chat_sessions` | Stores chat sessions linked to a user and optionally a machine. |
| `chat_messages` | Stores user/assistant messages within a chat session. |
| `knowledge_documents` | Stores metadata about knowledge-base documents. |

### 7.1 Relationship overview

```text
machines
 ├── sensor_readings
 ├── predictions ── model_versions
 │    └── risk_scores
 ├── risk_scores
 ├── alerts ── users (assigned_to / acknowledged_by)
 ├── maintenance_records ── users (created_by)
 └── chat_sessions ── users
      └── chat_messages

knowledge_documents
```

More precisely:

- One machine can have many sensor readings.
- One machine can have many predictions.
- Each prediction references one model version.
- A prediction can have associated risk-score records.
- One machine can have many risk scores.
- A machine can have many alerts; an alert may optionally reference a prediction.
- An alert may optionally reference users for assignment and acknowledgement.
- A machine can have many maintenance records; each record references the user who created it.
- A user can have many chat sessions.
- A chat session can optionally reference a machine and can contain many chat messages.
- `knowledge_documents` stores document metadata and is not directly connected to the other tables in this schema version.

## 8. Table details

The following descriptions summarize the schema's known design. For the authoritative column definitions and exact SQL types/defaults, refer to `docs/database/database-schema-v0.sql`.

### 8.1 `users`

**Purpose:** User identity and role metadata.

Key fields include:

- `id` — UUID primary key.
- `name` — user's display name.
- `email` — unique email address.
- `password_hash` — stored password hash; never store a plaintext password.
- `role` — restricted to `ADMIN`, `MAINTENANCE_MANAGER`, or `MAINTENANCE_ENGINEER`.
- `is_active` — active/inactive status.
- `created_at`, `updated_at` — timestamps.

Constraints and notes:

- `email` is unique.
- `role` is constrained to the three values above.
- The current schema does **not** include a `VIEWER` role.
- `updated_at` has a default, but the schema does not define an automatic update trigger. Application code or a future database trigger would need to update it when a record changes.

### 8.2 `machines`

**Purpose:** Identifies an engine/machine in a dataset.

Key fields include:

- `id` — UUID primary key.
- `machine_code` — unique machine identifier.
- `dataset_id` — dataset identifier, constrained to FD001–FD004.
- `engine_id` — positive engine number.

Constraints and notes:

- `machine_code` is unique.
- `engine_id` must be positive.
- `(dataset_id, engine_id)` is unique, so the same engine number may appear in a different dataset but not twice within the same dataset.

### 8.3 `sensor_readings`

**Purpose:** Stores sensor and operating-setting values by machine and cycle.

Key fields include:

- `id` — `BIGSERIAL` primary key.
- `machine_id` — foreign key to `machines.id`.
- `cycle` — positive cycle number.
- `op_setting_1`, `op_setting_2`, `op_setting_3` — operating settings.
- `sensor_1` through `sensor_21` — sensor measurements.
- `created_at` — insertion timestamp.

Constraints and indexes:

- `machine_id` references `machines.id` with `ON DELETE CASCADE`.
- `cycle` must be positive.
- `(machine_id, cycle)` is unique, preventing duplicate cycle records for the same machine.
- Index: `idx_sensor_readings_machine_cycle`.

### 8.4 `model_versions`

**Purpose:** Tracks registered model versions and their artifact metadata.

Key fields include:

- `id` — UUID primary key.
- Model name/type and dataset identifier.
- Version.
- Artifact URI.
- Feature and preprocessing version information.
- Active flag and timestamps.

Constraints and notes:

- `(model_name, version)` is unique.
- Predictions reference a model version.
- The exact allowed values for model type and dataset identifiers are defined in the SQL schema.

### 8.5 `predictions`

**Purpose:** Stores RUL prediction results for a machine at a particular cycle.

Key fields include:

- `id` — `BIGSERIAL` primary key.
- `machine_id` — machine foreign key.
- `model_version_id` — model-version foreign key.
- `cycle` — prediction cycle.
- `predicted_rul` — nonnegative predicted RUL.
- Optional lower/upper prediction bounds and `coverage_level`.
- `at_cap` — indicates whether the prediction is at the configured cap.
- `created_at` — timestamp.

Constraints and indexes:

- `(machine_id, model_version_id, cycle)` is unique.
- `predicted_rul` must be nonnegative.
- A check validates lower/upper bound consistency.
- A check constrains `coverage_level` to its permitted range.
- Indexes support machine/cycle and model-version lookups.
- `machine_id` references `machines.id` with `ON DELETE CASCADE`.
- `model_version_id` references `model_versions.id` using the default delete behavior (no cascade specified). A referenced model version therefore cannot normally be deleted while predictions still reference it.

### 8.6 `risk_scores`

**Purpose:** Stores a risk classification associated with a machine and prediction.

Key fields include:

- `id` — `BIGSERIAL` primary key.
- `machine_id` — machine foreign key.
- `prediction_id` — prediction foreign key.
- `risk_level` — `LOW`, `MEDIUM`, or `HIGH`.
- `rul_threshold` — nonnegative RUL threshold.
- Optional probability.
- `thresholds_version` and `created_at`.

Constraints and indexes:

- Probability, when provided, must be between 0 and 1.
- `risk_level` is restricted to `LOW`, `MEDIUM`, or `HIGH`.
- Indexes support machine and risk-level lookups.
- Both machine and prediction references use `ON DELETE CASCADE`.

**Integrity note:** The current schema does not enforce that `risk_scores.machine_id` is the same machine as the machine referenced by `risk_scores.prediction_id`. Application validation or a future schema enhancement could enforce this if required.

### 8.7 `alerts`

**Purpose:** Records machine alerts and their workflow status.

Key fields include:

- `id` — `BIGSERIAL` primary key.
- `machine_id` — machine foreign key.
- Optional `prediction_id`.
- Optional `assigned_to` and `acknowledged_by` user references.
- Alert type, severity, message, status, acknowledgement time, and creation time.

Constraints and relationships:

- Severity is restricted to `LOW`, `MEDIUM`, or `HIGH`.
- Status is restricted to `OPEN`, `ACKNOWLEDGED`, or `RESOLVED`.
- `OPEN` alerts must have a null `acknowledged_at`.
- `machine_id` uses `ON DELETE CASCADE`.
- `prediction_id`, `assigned_to`, and `acknowledged_by` use `ON DELETE SET NULL`.
- Indexes support status and machine lookups.

The current check does not require `acknowledged_at` to be non-null for every acknowledged or resolved alert.

### 8.8 `maintenance_records`

**Purpose:** Tracks maintenance work for a machine.

Key fields include:

- `id` — `BIGSERIAL` primary key.
- `machine_id` — machine foreign key.
- `created_by` — user foreign key.
- Title, description, action, status, schedule/completion times, and timestamps.

Constraints and relationships:

- Status is restricted to `OPEN`, `IN_PROGRESS`, `COMPLETED`, or `CANCELLED`.
- `completed_at` must not precede `scheduled_at` when both values are present.
- `machine_id` uses `ON DELETE CASCADE`.
- `created_by` references `users.id` with the default delete behavior; a user referenced by a maintenance record cannot normally be deleted while the reference exists.
- Index: machine lookup index.

### 8.9 `chat_sessions`

**Purpose:** Groups chat messages for a user and optionally a machine.

Key fields include:

- `id` — UUID primary key.
- `user_id` — user foreign key.
- Optional `machine_id` — machine foreign key.
- Title and timestamps.

Relationships:

- `user_id` references `users.id` with `ON DELETE CASCADE`.
- `machine_id` references `machines.id` with `ON DELETE SET NULL`.
- An index supports machine lookups.

### 8.10 `chat_messages`

**Purpose:** Stores individual messages in a chat session.

Key fields include:

- `id` — `BIGSERIAL` primary key.
- `session_id` — chat-session foreign key.
- `role` — `USER` or `ASSISTANT`.
- `content` — message text.
- `created_at` — timestamp.

Relationships and constraints:

- `session_id` references `chat_sessions.id` with `ON DELETE CASCADE`.
- Role is restricted to `USER` or `ASSISTANT`.
- An index supports session-based message retrieval.

### 8.11 `knowledge_documents`

**Purpose:** Stores metadata for documents that may later be used by the knowledge base.

Key fields include:

- `id` — UUID primary key.
- `title`, `source`, `source_url`, `document_type`, `description`.
- Creation and update timestamps.

Indexes and scope notes:

- An index supports document-type lookups.
- This table stores **document metadata**. The current schema does not itself define document chunks, vector embeddings, or vector-search indexes.

## 9. Foreign-key relationship reference

| Child table and column | References | Delete behavior |
|---|---|---|
| `sensor_readings.machine_id` | `machines.id` | CASCADE |
| `predictions.machine_id` | `machines.id` | CASCADE |
| `predictions.model_version_id` | `model_versions.id` | Default / NO ACTION |
| `risk_scores.machine_id` | `machines.id` | CASCADE |
| `risk_scores.prediction_id` | `predictions.id` | CASCADE |
| `alerts.machine_id` | `machines.id` | CASCADE |
| `alerts.prediction_id` | `predictions.id` | SET NULL |
| `alerts.assigned_to` | `users.id` | SET NULL |
| `alerts.acknowledged_by` | `users.id` | SET NULL |
| `maintenance_records.machine_id` | `machines.id` | CASCADE |
| `maintenance_records.created_by` | `users.id` | Default / NO ACTION |
| `chat_sessions.user_id` | `users.id` | CASCADE |
| `chat_sessions.machine_id` | `machines.id` | SET NULL |
| `chat_messages.session_id` | `chat_sessions.id` | CASCADE |

`knowledge_documents` has no foreign-key relationship to these tables in the current schema.

## 10. Verification queries

Run these queries in pgAdmin's Query Tool or in a `psql` session connected to `predictive_maintenance`.

### 10.1 List tables

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

### 10.2 Count records in each table

```sql
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL SELECT 'machines', COUNT(*) FROM machines
UNION ALL SELECT 'sensor_readings', COUNT(*) FROM sensor_readings
UNION ALL SELECT 'model_versions', COUNT(*) FROM model_versions
UNION ALL SELECT 'predictions', COUNT(*) FROM predictions
UNION ALL SELECT 'risk_scores', COUNT(*) FROM risk_scores
UNION ALL SELECT 'alerts', COUNT(*) FROM alerts
UNION ALL SELECT 'maintenance_records', COUNT(*) FROM maintenance_records
UNION ALL SELECT 'chat_sessions', COUNT(*) FROM chat_sessions
UNION ALL SELECT 'chat_messages', COUNT(*) FROM chat_messages
UNION ALL SELECT 'knowledge_documents', COUNT(*) FROM knowledge_documents
ORDER BY table_name;
```

The expected counts depend on whether the seed script has been run and whether development data has subsequently been added. Previously observed seed counts were:

| Table | Previously observed count |
|---|---:|
| `users` | 1 |
| `machines` | 1 |
| `sensor_readings` | 3 |
| `model_versions` | 1 |
| `predictions` | 3 |
| `risk_scores` | 3 |
| `knowledge_documents` | 1 |
| `alerts` | 0 |
| `maintenance_records` | 0 |
| `chat_sessions` | 0 |
| `chat_messages` | 0 |

These are historical setup observations, not a guarantee of the current database state.

### 10.3 Inspect sensor readings

```sql
SELECT *
FROM sensor_readings
ORDER BY machine_id, cycle
LIMIT 10;
```

### 10.4 Inspect predictions

```sql
SELECT
    p.id,
    m.machine_code,
    p.cycle,
    p.predicted_rul,
    p.created_at
FROM predictions AS p
JOIN machines AS m ON m.id = p.machine_id
ORDER BY p.created_at DESC
LIMIT 20;
```

### 10.5 Inspect foreign keys

```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.constraint_schema = kcu.constraint_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
 AND ccu.constraint_schema = tc.constraint_schema
JOIN information_schema.referential_constraints AS rc
  ON rc.constraint_name = tc.constraint_name
 AND rc.constraint_schema = tc.constraint_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;
```

### 10.6 Inspect columns and data types

```sql
SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

## 11. Troubleshooting

### PostgreSQL port 5432 is already in use

Another PostgreSQL service may already be running on the computer.

In Windows CMD, identify the process listening on port 5432:

```bat
netstat -ano | findstr :5432
```

The final column contains a PID. To identify it:

```bat
tasklist /FI "PID eq <PID>"
```

Replace `<PID>` with the actual process ID. Do not terminate a process until you know what it is. If a local PostgreSQL installation is already using port 5432, either stop it safely when appropriate or configure the Docker port mapping to use another host port.

### Container is not healthy or will not start

```bat
docker compose ps
docker compose logs
```

Check the logs for configuration errors, port conflicts, invalid environment variables, or a failed database initialization.

### Authentication failed

Confirm the configured database name, username, password, and port in the Compose file or environment configuration. Do not assume that the earlier development password is still current.

### `psql` is not recognized

Use `docker compose exec` or `docker exec` to run `psql` inside the PostgreSQL container, or install the PostgreSQL client tools on the host.

### SQL file cannot be found

Commands using a relative path must be run from the project root. Check the files exist:

```bat
dir docs\database
```

### Tables do not appear in pgAdmin

Make sure pgAdmin is connected to the `predictive_maintenance` database, not the default `postgres` database. Refresh the `public` schema and its Tables node.

### Seed script fails due to duplicate data

Read the seed script to understand whether it is safe to run more than once. Do not repeatedly execute a non-idempotent seed script on the same database. If resetting a development database is necessary, first confirm that no data needs to be preserved.

## 12. Development and safety notes

- Keep database passwords and other secrets out of committed source files.
- Use development seed records only for local testing.
- Back up data before destructive schema changes.
- Avoid deleting referenced parent records without understanding their foreign-key delete behavior.
- Keep schema changes in version-controlled SQL migration or schema files.
- Coordinate schema changes with the team so backend and frontend work against the same version.
- The current schema provides data structures; it does not by itself implement authentication, authorization, model execution, or application-level business rules.

## 13. Setup completion checklist

- [ ] Docker Compose PostgreSQL service starts successfully.
- [ ] `predictive_maintenance` database is accessible.
- [ ] `database-schema-v0.sql` has been applied.
- [ ] All 11 expected tables exist.
- [ ] Foreign keys and indexes are present.
- [ ] `seed-v0.sql` has been applied if development sample data is required.
- [ ] Verification queries execute successfully.
- [ ] Team members have confirmed their local connection settings.

---

**Primary source of truth:** `docs/database/database-schema-v0.sql` and `docs/database/seed-v0.sql` in the project repository. If this document and the SQL files ever differ, follow the current SQL files and update this documentation.
