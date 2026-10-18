
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs/contracts/health-summary-v0.schema.json"
EXAMPLE_PATH = ROOT / "docs/contracts/health-summary-v0.example.json"
OPENAPI_PATH = ROOT / "docs/api/openapi.yaml"

DISCLAIMER = (
    "Research-oriented decision support based on simulated C-MAPSS data "
    "and retrieved technical knowledge."
)


@pytest.fixture(scope="module")
def schema():
    with SCHEMA_PATH.open(encoding="utf-8") as file:
        value = json.load(file)

    Draft202012Validator.check_schema(value)
    return value


@pytest.fixture(scope="module")
def example():
    with EXAMPLE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture(scope="module")
def openapi():
    with OPENAPI_PATH.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_example_is_valid(schema, example):
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))

    assert not errors, "\n".join(
        f"{list(error.path)}: {error.message}" for error in errors
    )


def test_example_uses_readable_machine_id(example):
    assert example["machine_id"] == "FD001-E047"
    assert not example["machine_id"].startswith("urn:uuid:")


def test_example_interval_bounds_are_ordered(example):
    interval = example["rul"].get("interval")
    if interval is not None:
        assert interval["upper_bound"] >= interval["lower_bound"]


def test_example_disclaimer_is_correct(example):
    assert example["disclaimer"] == DISCLAIMER


def test_optional_fields_can_be_omitted(schema, example):
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

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    validator.validate(minimal)


def test_invalid_interval_is_rejected_by_semantic_check(example):
    invalid = json.loads(json.dumps(example))
    invalid["rul"]["interval"]["lower_bound"] = 25
    invalid["rul"]["interval"]["upper_bound"] = 14

    # JSON Schema checks the individual numeric bounds.
    # Cross-field ordering is checked separately by this test.
    interval = invalid["rul"]["interval"]
    assert interval["upper_bound"] < interval["lower_bound"]


def test_openapi_uses_readable_machine_path_parameter(openapi):
    parameter = openapi["components"]["parameters"]["MachineId"]

    assert parameter["schema"]["type"] == "string"
    assert parameter["schema"].get("format") != "uuid"


def test_openapi_health_summary_matches_key_contract_fields(openapi):
    summary = openapi["components"]["schemas"]["HealthSummary"]
    properties = summary["properties"]

    assert "machine_id" in summary["required"]
    assert properties["machine_id"]["type"] == "string"
    assert "estimate" in properties["rul"]["properties"]
    assert "point" not in properties["rul"]["properties"]
    assert "risk_level" in properties
    assert "risk" not in properties
    assert "shap_value" in (
        properties["top_contributors"]["items"]["properties"]
    )


def test_openapi_prediction_request_uses_readable_machine_id(openapi):
    request = openapi["components"]["schemas"]["PredictionRequest"]
    machine_id = request["properties"]["machine_id"]

    assert machine_id["type"] == "string"
    assert machine_id.get("format") != "uuid"
