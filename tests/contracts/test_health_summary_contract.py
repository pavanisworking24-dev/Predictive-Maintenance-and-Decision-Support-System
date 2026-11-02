import json
import re
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs/contracts/health-summary-v0.schema.json"
EXAMPLE_PATH = ROOT / "docs/contracts/health-summary-v0.example.json"
OPENAPI_PATH = ROOT / "docs/api/openapi.yaml"
DB_SCHEMA_PATH = ROOT / "docs/database/database-schema-v0.sql"

DISCLAIMER = (
    "Research-oriented decision support based on simulated C-MAPSS data "
    "and retrieved technical knowledge."
)


# Tolerance for rounding when comparing a probability with a coverage level.
PROBABILITY_TOLERANCE = 0.02


def probability_consistency_errors(interval, probability):
    """Check that P(RUL <= N) agrees with the conformal interval.

    Both numbers come from the same calibration residuals, so they cannot
    contradict each other:
    - If N is at or above the interval's upper bound, at least `coverage_level`
      of the probability mass lies at or below N, so P(RUL <= N) >= coverage.
    - If N is below the interval's lower bound, at most `1 - coverage_level`
      of the mass lies at or below N, so P(RUL <= N) <= 1 - coverage.
    """
    errors = []
    threshold = probability["threshold_cycles"]
    value = probability["probability"]
    coverage = interval["coverage_level"]

    if threshold >= interval["upper_bound"] and value < coverage - PROBABILITY_TOLERANCE:
        errors.append(
            f"P(RUL <= {threshold}) = {value} is too low: the threshold is at or above "
            f"the interval upper bound ({interval['upper_bound']}), so it should be "
            f"at least the coverage level ({coverage})"
        )
    if threshold < interval["lower_bound"] and value > (1 - coverage) + PROBABILITY_TOLERANCE:
        errors.append(
            f"P(RUL <= {threshold}) = {value} is too high: the threshold is below "
            f"the interval lower bound ({interval['lower_bound']}), so it should be "
            f"at most {round(1 - coverage, 4)}"
        )
    return errors


# ---------------------------------------------------------------------------
# Semantic checks
#
# JSON Schema validates the shape of each field, but it cannot compare two
# fields with each other. These rules are checked here. The backend should
# call the same function before returning or storing a summary.
# ---------------------------------------------------------------------------
def semantic_errors(summary):
    """Return a list of cross-field rule violations (empty list = valid)."""
    errors = []

    rul = summary.get("rul", {})
    interval = rul.get("interval")
    if interval is not None:
        lower = interval["lower_bound"]
        upper = interval["upper_bound"]
        if upper < lower:
            errors.append(f"interval upper_bound ({upper}) is below lower_bound ({lower})")
        else:
            estimate = rul["estimate"]
            if not (lower <= estimate <= upper):
                errors.append(
                    f"rul.estimate ({estimate}) is outside the interval [{lower}, {upper}]"
                )

    probability = summary.get("rul_threshold_probability")
    if interval is not None and probability is not None:
        errors.extend(probability_consistency_errors(interval, probability))

    has_risk = "risk_level" in summary
    has_version = "thresholds_version" in summary
    if has_risk and not has_version:
        errors.append("risk_level is present but thresholds_version is missing")
    if has_version and not has_risk:
        errors.append("thresholds_version is present but risk_level is missing")

    return errors


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def schema():
    with SCHEMA_PATH.open(encoding="utf-8") as file:
        value = json.load(file)

    Draft202012Validator.check_schema(value)
    return value


@pytest.fixture(scope="module")
def validator(schema):
    return Draft202012Validator(schema, format_checker=FormatChecker())


@pytest.fixture(scope="module")
def example():
    with EXAMPLE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture(scope="module")
def openapi():
    with OPENAPI_PATH.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def resolve_ref(openapi, node):
    """Follow a local $ref such as '#/components/schemas/RULEstimate'."""
    while isinstance(node, dict) and "$ref" in node:
        target = openapi
        for part in node["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        node = target
    return node


def copy_of(value):
    return json.loads(json.dumps(value))


def db_risk_levels():
    """Read the allowed risk_level values from the risk_scores CHECK in the SQL."""
    sql = DB_SCHEMA_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"risk_level\s+VARCHAR\(\d+\)\s+NOT NULL\s+CHECK\s*\(\s*"
        r"risk_level\s+IN\s*\(([^)]*)\)",
        sql,
    )
    assert match, "Could not find the risk_level CHECK constraint in the SQL schema"
    return re.findall(r"'([A-Z_]+)'", match.group(1))


# ---------------------------------------------------------------------------
# Example file
# ---------------------------------------------------------------------------
def test_example_is_valid(validator, example):
    errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))

    assert not errors, "\n".join(f"{list(error.path)}: {error.message}" for error in errors)


def test_example_passes_semantic_checks(example):
    assert semantic_errors(example) == []


def test_example_uses_readable_machine_id(example):
    assert example["machine_id"] == "FD001-E047"
    assert not example["machine_id"].startswith("urn:uuid:")


def test_example_disclaimer_is_correct(example):
    assert example["disclaimer"] == DISCLAIMER


def test_optional_fields_can_be_omitted(validator, example):
    minimal = {
        key: example[key]
        for key in (
            "machine_id",
            "dataset_id",
            "cycle",
            "model_version",
            "generated_at",
            "disclaimer",
        )
    }
    minimal["rul"] = {
        "estimate": example["rul"]["estimate"],
        "at_cap": example["rul"]["at_cap"],
    }

    validator.validate(minimal)
    assert semantic_errors(minimal) == []


# ---------------------------------------------------------------------------
# Semantic rules (these tests exercise real logic)
# ---------------------------------------------------------------------------
def test_reversed_interval_is_detected(example):
    invalid = copy_of(example)
    invalid["rul"]["interval"]["lower_bound"] = 25
    invalid["rul"]["interval"]["upper_bound"] = 14

    errors = semantic_errors(invalid)

    assert any("upper_bound" in message for message in errors)


def test_estimate_outside_interval_is_detected(example):
    invalid = copy_of(example)
    invalid["rul"]["estimate"] = 60  # interval is [14, 23]

    errors = semantic_errors(invalid)

    assert any("outside the interval" in message for message in errors)


def test_probability_below_coverage_is_detected(example):
    # The original example had RUL 18, interval 14-23 (90%) and P(RUL <= 30) = 0.81,
    # which is impossible: 30 is above the interval, so the probability must be >= 0.90.
    invalid = copy_of(example)
    invalid["rul_threshold_probability"]["probability"] = 0.81

    errors = semantic_errors(invalid)

    assert any("too low" in message for message in errors)


def test_probability_above_complement_below_interval_is_detected(example):
    invalid = copy_of(example)
    invalid["rul_threshold_probability"]["threshold_cycles"] = 10  # below lower bound 14
    invalid["rul_threshold_probability"]["probability"] = 0.6

    errors = semantic_errors(invalid)

    assert any("too high" in message for message in errors)


def test_probability_inside_interval_range_is_not_constrained(example):
    valid = copy_of(example)
    valid["rul_threshold_probability"]["threshold_cycles"] = 20  # inside [14, 23]
    valid["rul_threshold_probability"]["probability"] = 0.7

    assert semantic_errors(valid) == []


def test_risk_level_requires_thresholds_version(example):
    invalid = copy_of(example)
    del invalid["thresholds_version"]

    errors = semantic_errors(invalid)

    assert any("thresholds_version is missing" in message for message in errors)


def test_thresholds_version_requires_risk_level(example):
    invalid = copy_of(example)
    del invalid["risk_level"]

    errors = semantic_errors(invalid)

    assert any("risk_level is missing" in message for message in errors)


# ---------------------------------------------------------------------------
# JSON Schema rejects invalid values
# ---------------------------------------------------------------------------
def test_schema_rejects_critical_risk_level(validator, example):
    invalid = copy_of(example)
    invalid["risk_level"] = "CRITICAL"

    assert list(validator.iter_errors(invalid)), "CRITICAL must not be accepted"


def test_schema_rejects_unknown_top_level_field(validator, example):
    invalid = copy_of(example)
    invalid["failure_probability"] = {"value": 0.8}

    assert list(validator.iter_errors(invalid))


# ---------------------------------------------------------------------------
# OpenAPI matches the JSON Schema
# ---------------------------------------------------------------------------
def test_openapi_uses_readable_machine_path_parameter(openapi):
    parameter = openapi["components"]["parameters"]["MachineId"]

    assert parameter["schema"]["type"] == "string"
    assert parameter["schema"].get("format") != "uuid"


def test_openapi_health_summary_matches_key_contract_fields(openapi):
    summary = openapi["components"]["schemas"]["HealthSummary"]
    properties = summary["properties"]

    assert "machine_id" in summary["required"]
    assert properties["machine_id"]["type"] == "string"

    rul = resolve_ref(openapi, properties["rul"])
    assert "estimate" in rul["properties"]
    assert "point" not in rul["properties"]

    assert "risk_level" in properties
    assert "thresholds_version" in properties
    assert "risk" not in properties

    contributor = resolve_ref(openapi, properties["top_contributors"]["items"])
    assert "shap_value" in contributor["properties"]


def test_openapi_and_schema_have_same_top_level_fields(openapi, schema):
    summary = openapi["components"]["schemas"]["HealthSummary"]

    assert set(summary["properties"]) == set(schema["properties"])
    assert set(summary["required"]) == set(schema["required"])


def test_risk_levels_match_across_schema_openapi_and_database(openapi, schema):
    schema_levels = schema["properties"]["risk_level"]["enum"]
    openapi_levels = openapi["components"]["schemas"]["HealthSummary"]["properties"]["risk_level"][
        "enum"
    ]

    assert set(schema_levels) == set(openapi_levels) == set(db_risk_levels())


def test_openapi_prediction_request_uses_readable_machine_id(openapi):
    request = openapi["components"]["schemas"]["PredictionRequest"]
    machine_id = request["properties"]["machine_id"]

    assert machine_id["type"] == "string"
    assert machine_id.get("format") != "uuid"
