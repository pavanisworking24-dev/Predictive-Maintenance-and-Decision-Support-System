"""Contract tests for the OpenAPI document as a whole.

They check that the planned API surface is complete, that authentication and
role rules are declared, that the document is internally consistent, and that
its enums match the database CHECK constraints.
"""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs/api/openapi.yaml"
DB_SCHEMA_PATH = ROOT / "docs/database/database-schema-v0.sql"

HTTP_METHODS = ("get", "post", "put", "patch", "delete")

ALL_ROLES = {"ADMIN", "MAINTENANCE_MANAGER", "MAINTENANCE_ENGINEER"}

# Every endpoint the scope (section 5.3) requires, plus the extra ones in the
# contract. Paths follow docs/api/openapi.yaml.
EXPECTED_OPERATIONS = {
    ("POST", "/auth/login"),
    ("GET", "/health"),
    ("GET", "/machines"),
    ("GET", "/machines/{machine_id}"),
    ("GET", "/machines/{machine_id}/sensor-readings"),
    ("GET", "/machines/{machine_id}/predictions"),
    ("GET", "/machines/{machine_id}/health-summary"),
    ("GET", "/machines/{machine_id}/explanation"),
    ("POST", "/predictions"),
    ("GET", "/risk"),
    ("GET", "/risk/high"),
    ("GET", "/maintenance"),
    ("POST", "/maintenance"),
    ("PUT", "/maintenance/{maintenance_id}"),
    ("GET", "/alerts"),
    ("PATCH", "/alerts/{alert_id}"),
    ("POST", "/chat"),
    ("GET", "/chat/sessions"),
    ("GET", "/metrics"),
    ("GET", "/reports/fleet"),
    ("GET", "/thresholds"),
    ("POST", "/thresholds"),
    ("GET", "/users"),
    ("POST", "/users"),
    ("PATCH", "/users/{user_id}"),
    ("GET", "/models"),
    ("POST", "/models/{model_version_id}/activate"),
    ("GET", "/knowledge/documents"),
    ("POST", "/knowledge/documents"),
    ("DELETE", "/knowledge/documents/{document_id}"),
}

PUBLIC_OPERATIONS = {("POST", "/auth/login"), ("GET", "/health")}

# Permission matrix, scope section 5.1
RESTRICTED_OPERATIONS = {
    ("POST", "/maintenance"): {"ADMIN", "MAINTENANCE_ENGINEER"},
    ("PUT", "/maintenance/{maintenance_id}"): {"ADMIN", "MAINTENANCE_ENGINEER"},
    ("PATCH", "/alerts/{alert_id}"): {"ADMIN", "MAINTENANCE_MANAGER"},
    # Administration: users, thresholds, model version, knowledge base (scope 5.1)
    ("POST", "/thresholds"): {"ADMIN"},
    ("GET", "/users"): {"ADMIN"},
    ("POST", "/users"): {"ADMIN"},
    ("PATCH", "/users/{user_id}"): {"ADMIN"},
    ("GET", "/models"): {"ADMIN"},
    ("POST", "/models/{model_version_id}/activate"): {"ADMIN"},
    ("GET", "/knowledge/documents"): {"ADMIN"},
    ("POST", "/knowledge/documents"): {"ADMIN"},
    ("DELETE", "/knowledge/documents/{document_id}"): {"ADMIN"},
    # Logs and monitoring (scope 5.1)
    ("GET", "/metrics"): {"ADMIN"},
}


@pytest.fixture(scope="module")
def openapi():
    with OPENAPI_PATH.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="module")
def db_sql():
    return DB_SCHEMA_PATH.read_text(encoding="utf-8")


def operations(openapi):
    """Yield (METHOD, path, operation) for every operation in the document."""
    for path, item in openapi["paths"].items():
        for method in HTTP_METHODS:
            if method in item:
                yield method.upper(), path, item[method]


def deref(openapi, node):
    while isinstance(node, dict) and "$ref" in node:
        target = openapi
        for part in node["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        node = target
    return node


def is_public(operation):
    return operation.get("security") == []


def db_table_columns(sql, table):
    """Return the column names of a table in the SQL schema."""
    table_match = re.search(rf"CREATE TABLE {table} \((.*?)\n\);", sql, re.DOTALL)
    assert table_match, f"table {table} not found in the SQL schema"
    columns = set()
    for line in table_match.group(1).splitlines():
        match = re.match(r"    ([a-z_0-9]+) [A-Za-z]", line)
        if match and match.group(1) not in {"constraint", "check", "unique", "primary"}:
            columns.add(match.group(1))
    return columns


def db_check_values(sql, table, column):
    """Return the values of a column's CHECK (column IN (...)) constraint."""
    table_match = re.search(rf"CREATE TABLE {table} \((.*?)\n\);", sql, re.DOTALL)
    assert table_match, f"table {table} not found in the SQL schema"
    column_match = re.search(
        rf"{column}\s+VARCHAR\(\d+\)[^;]*?CHECK\s*\(\s*{column}\s+IN\s*\(([^)]*)\)",
        table_match.group(1),
        re.DOTALL,
    )
    assert column_match, f"no IN-list CHECK on {table}.{column}"
    return set(re.findall(r"'([A-Za-z0-9_]+)'", column_match.group(1)))


# ---------------------------------------------------------------------------
# Completeness and consistency
# ---------------------------------------------------------------------------
def test_expected_operations_are_defined(openapi):
    defined = {(method, path) for method, path, _ in operations(openapi)}

    assert EXPECTED_OPERATIONS <= defined, sorted(EXPECTED_OPERATIONS - defined)


def test_no_unexpected_operations(openapi):
    defined = {(method, path) for method, path, _ in operations(openapi)}

    assert defined <= EXPECTED_OPERATIONS, sorted(defined - EXPECTED_OPERATIONS)


def test_all_references_resolve(openapi):
    unresolved = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "$ref":
                    try:
                        deref(openapi, {"$ref": value})
                    except (KeyError, TypeError):
                        unresolved.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(openapi)

    assert not unresolved, unresolved


def test_operation_ids_are_unique(openapi):
    ids = [operation["operationId"] for _, _, operation in operations(openapi)]

    assert len(ids) == len(set(ids))


def test_path_parameters_are_declared(openapi):
    for method, path, operation in operations(openapi):
        in_path = set(re.findall(r"\{(\w+)\}", path))
        parameters = openapi["paths"][path].get("parameters", []) + operation.get(
            "parameters", []
        )
        declared = {
            deref(openapi, p)["name"]
            for p in parameters
            if deref(openapi, p)["in"] == "path"
        }

        assert in_path == declared, f"{method} {path}: {in_path} vs {declared}"


# ---------------------------------------------------------------------------
# Authentication and roles
# ---------------------------------------------------------------------------
def test_bearer_scheme_and_global_security(openapi):
    scheme = openapi["components"]["securitySchemes"]["bearerAuth"]

    assert scheme["type"] == "http"
    assert scheme["scheme"] == "bearer"
    assert scheme["bearerFormat"] == "JWT"
    assert openapi["security"] == [{"bearerAuth": []}]


def test_only_login_and_health_are_public(openapi):
    public = {
        (method, path) for method, path, op in operations(openapi) if is_public(op)
    }

    assert public == PUBLIC_OPERATIONS


def test_protected_operations_declare_401(openapi):
    for method, path, operation in operations(openapi):
        if not is_public(operation):
            assert "401" in operation["responses"], f"{method} {path} lacks 401"


def test_restricted_operations_match_permission_matrix(openapi):
    restricted = {
        (method, path): set(operation["x-allowed-roles"])
        for method, path, operation in operations(openapi)
        if "x-allowed-roles" in operation
    }

    assert restricted == RESTRICTED_OPERATIONS


def test_restricted_operations_declare_403(openapi):
    for method, path, operation in operations(openapi):
        if "x-allowed-roles" in operation:
            assert "403" in operation["responses"], f"{method} {path} lacks 403"


# ---------------------------------------------------------------------------
# Contract matches the database
# ---------------------------------------------------------------------------
def test_user_roles_match_database(openapi, db_sql):
    api_roles = set(openapi["components"]["schemas"]["UserRole"]["enum"])

    assert api_roles == ALL_ROLES
    assert api_roles == db_check_values(db_sql, "users", "role")


def test_dataset_ids_match_database(openapi, db_sql):
    api_values = set(openapi["components"]["schemas"]["DatasetId"]["enum"])

    assert api_values == db_check_values(db_sql, "machines", "dataset_id")


def test_alert_enums_match_database(openapi, db_sql):
    schemas = openapi["components"]["schemas"]

    assert set(schemas["AlertStatus"]["enum"]) == db_check_values(
        db_sql, "alerts", "status"
    )
    assert set(schemas["RiskLevel"]["enum"]) == db_check_values(
        db_sql, "alerts", "severity"
    )


def test_maintenance_status_matches_database(openapi, db_sql):
    api_values = set(openapi["components"]["schemas"]["MaintenanceStatus"]["enum"])

    assert api_values == db_check_values(db_sql, "maintenance_records", "status")


def test_alert_update_only_allows_acknowledged_or_resolved(openapi):
    status = openapi["components"]["schemas"]["AlertUpdate"]["properties"]["status"]

    assert set(status["enum"]) == {"ACKNOWLEDGED", "RESOLVED"}


def test_prediction_id_matches_bigserial(openapi):
    prediction_id = openapi["components"]["schemas"]["Prediction"]["properties"][
        "prediction_id"
    ]

    assert prediction_id["type"] == "integer"
    assert prediction_id["format"] == "int64"


def test_chat_response_requires_disclaimer(openapi):
    chat = openapi["components"]["schemas"]["ChatResponse"]

    assert "disclaimer" in chat["required"]
    assert "sources" in chat["required"]


# ---------------------------------------------------------------------------
# Administration, reports and monitoring
# ---------------------------------------------------------------------------
def test_ingestion_status_matches_database(openapi, db_sql):
    api_values = set(openapi["components"]["schemas"]["IngestionStatus"]["enum"])

    assert api_values == db_check_values(
        db_sql, "knowledge_documents", "ingestion_status"
    )


def test_threshold_config_fields_exist_in_database(openapi, db_sql):
    properties = set(openapi["components"]["schemas"]["ThresholdConfig"]["properties"])
    columns = db_table_columns(db_sql, "risk_threshold_configs")

    assert properties <= columns, sorted(properties - columns)


def test_threshold_create_requires_every_tunable_field(openapi):
    schema = openapi["components"]["schemas"]["ThresholdConfigCreate"]

    assert set(schema["required"]) == {
        "version",
        "horizon_cycles",
        "high_rul_max",
        "medium_rul_max",
        "high_probability_min",
        "medium_probability_min",
        "alert_rul_threshold",
    }


def test_model_version_fields_exist_in_database(openapi, db_sql):
    properties = set(openapi["components"]["schemas"]["ModelVersion"]["properties"])
    columns = db_table_columns(db_sql, "model_versions") | {"model_version_id"}

    assert properties <= columns, sorted(properties - columns)


def test_user_schema_never_exposes_password_hash(openapi):
    user = openapi["components"]["schemas"]["User"]

    assert "password" not in user["properties"]
    assert "password_hash" not in user["properties"]


def test_every_role_can_read_thresholds_and_fleet_report(openapi):
    for method, path, operation in operations(openapi):
        if (method, path) in {("GET", "/thresholds"), ("GET", "/reports/fleet")}:
            assert "x-allowed-roles" not in operation


def test_risk_threshold_table_has_single_active_index(db_sql):
    assert "uq_risk_threshold_configs_one_active" in db_sql
    assert "REFERENCES risk_threshold_configs(version)" in db_sql