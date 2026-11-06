"""The implemented auth/users routes must match docs/api/openapi.yaml."""

from pathlib import Path

import pytest
from app.main import app

yaml = pytest.importorskip("yaml")

OPENAPI_PATH = Path(__file__).resolve().parents[2] / "docs/api/openapi.yaml"
PREFIX = "/api/v1"


def contract_operations(prefixes):
    spec = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    return {
        (method.upper(), path)
        for path, item in spec["paths"].items()
        if path.startswith(prefixes)
        for method in ("get", "post", "put", "patch", "delete")
        if method in item
    }


def implemented_operations(prefixes):
    # FastAPI's generated schema lists every mounted route, regardless of how
    # routers are included.
    found = set()
    for path, item in app.openapi()["paths"].items():
        if not path.startswith(PREFIX):
            continue
        relative = path.removeprefix(PREFIX)
        if relative.startswith(prefixes):
            found |= {(method.upper(), relative) for method in item}
    return found


def test_auth_and_users_routes_match_contract():
    prefixes = ("/auth", "/users")

    assert implemented_operations(prefixes) == contract_operations(prefixes)
