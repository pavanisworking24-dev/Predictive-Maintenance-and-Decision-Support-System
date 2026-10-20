#!/usr/bin/env bash
# Verifies the Docker Compose database after:
#   docker compose up -d --wait
#
# Run from anywhere inside the repository (Git Bash, WSL, Linux, macOS, CI):
#   bash scripts/check_db.sh
set -Eeuo pipefail

# Git Bash on Windows rewrites arguments that look like Unix paths into
# C:/Program Files/Git/... This stops that; it has no effect elsewhere.
export MSYS_NO_PATHCONV=1

# Work from the repository root so relative paths are correct.
cd "$(dirname "$0")/.."

EXPECTED_TABLES=13
EXPECTED_SEED="1,1,3,1,3,3,1"
SEED_FILE="docs/database/seed-v0.sql"
ACTIVE_MODEL_INDEX="uq_model_versions_one_active_per_dataset"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

# Run SQL (first argument) inside the postgres container.
q() {
  docker compose exec -T postgres sh -c \
    'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -tA' \
    <<<"$1"
}

# --------------------------------------------------
echo "0. Docker connectivity"
# --------------------------------------------------
command -v docker >/dev/null 2>&1 ||
  fail "Docker CLI was not found. Install Docker Desktop or add Docker to PATH."

if ! docker info >/dev/null 2>&1; then
  cat >&2 <<'MSG'
FAIL: Cannot connect to the Docker daemon.

Try these steps:
  1. Start Docker Desktop and wait until its engine is running.
  2. Run: docker context ls
  3. Run: docker info

If DOCKER_HOST points to a stale socket in Git Bash, try:
  unset DOCKER_HOST
  unset DOCKER_CONTEXT
  docker info

Then run this script again.
MSG
  exit 1
fi

docker compose ps --status running --services 2>/dev/null | grep -qx postgres ||
  fail "the postgres service is not running. Run: docker compose up -d --wait"
echo "   OK (Docker reachable, postgres running)"

# --------------------------------------------------
echo "1. Table count"
# --------------------------------------------------
tables="$(q "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")" ||
  fail "could not query the table count"
[[ "$tables" == "$EXPECTED_TABLES" ]] ||
  fail "expected $EXPECTED_TABLES tables, found $tables. The database may have been created from an older schema: docker compose down -v && docker compose up -d --wait"
echo "   OK ($tables tables)"

# --------------------------------------------------
echo "2. pgvector extension"
# --------------------------------------------------
vec="$(q "SELECT count(*) FROM pg_extension WHERE extname = 'vector';")" ||
  fail "could not query installed extensions"
[[ "$vec" == "1" ]] || fail "the pgvector extension is not installed"
echo "   OK"

snapshot() {
  q "SELECT (SELECT count(*) FROM users) || ',' || (SELECT count(*) FROM machines) || ',' || (SELECT count(*) FROM sensor_readings) || ',' || (SELECT count(*) FROM model_versions) || ',' || (SELECT count(*) FROM predictions) || ',' || (SELECT count(*) FROM risk_scores) || ',' || (SELECT count(*) FROM knowledge_documents);"
}

# --------------------------------------------------
echo "3. Seed data (users,machines,readings,models,predictions,risks,documents)"
# --------------------------------------------------
before="$(snapshot)" || fail "could not query seed counts"
[[ "$before" == "$EXPECTED_SEED" ]] ||
  fail "unexpected seed counts: $before (expected $EXPECTED_SEED)"
echo "   OK ($before)"

# --------------------------------------------------
echo "4. Seed script is idempotent (run it a second time)"
# --------------------------------------------------
[[ -f "$SEED_FILE" ]] || fail "$SEED_FILE not found"
# Streamed through stdin, so no path inside the container is needed.
docker compose exec -T postgres sh -c \
  'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -q' \
  < "$SEED_FILE" >/dev/null ||
  fail "the seed script failed on its second run"
after="$(snapshot)" || fail "could not query counts after rerunning the seed"
[[ "$before" == "$after" ]] ||
  fail "the seed changed row counts: $before -> $after"
echo "   OK (counts unchanged)"

# --------------------------------------------------
echo "5. Only one active model per dataset"
# --------------------------------------------------
# The test insert runs inside a DO block, so it never leaves a row behind.
# It passes only if the partial unique index rejects it; the insert being
# accepted, or being rejected by any other constraint, is a failure.
second_active_sql="$(cat <<SQL
DO \$\$
DECLARE c text;
BEGIN
  INSERT INTO model_versions (model_name, model_type, dataset_id, version, is_active)
  VALUES ('check-second-active', 'XGBoost', 'FD001', 'check-test', TRUE);
  RAISE EXCEPTION 'a second active FD001 model was accepted';
EXCEPTION WHEN unique_violation THEN
  GET STACKED DIAGNOSTICS c = CONSTRAINT_NAME;
  IF c IS DISTINCT FROM '$ACTIVE_MODEL_INDEX' THEN
    RAISE EXCEPTION 'rejected by an unexpected constraint: %', c;
  END IF;
END \$\$;
SQL
)"
if ! step5_output="$(q "$second_active_sql" 2>&1)"; then
  echo "$step5_output" | grep -v "collation" >&2 || true
  fail "the active-model rule is not enforced as expected. If the index $ACTIVE_MODEL_INDEX is missing, the database was built from an older schema: docker compose down -v && docker compose up -d --wait"
fi
echo "   OK (second active model rejected by $ACTIVE_MODEL_INDEX)"

echo
echo "All database checks passed."