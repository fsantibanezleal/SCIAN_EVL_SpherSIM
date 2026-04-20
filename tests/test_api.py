"""
Route-level tests for service-introspection endpoints.

Covers ``GET /api/health`` and ``GET /api/version``. These endpoints are
used by uptime monitors and deploy-verification smoke tests, so a broken
payload here breaks operational tooling — worth a guard.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient

from app import __version__
from app.main import app, APP_TITLE


client = TestClient(app)


def test_health_endpoint_returns_ok():
    """GET /api/health returns HTTP 200 with the stable status payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_endpoint_matches_module_constant():
    """GET /api/version returns HTTP 200 with version == app.__version__."""
    response = client.get("/api/version")
    assert response.status_code == 200

    payload = response.json()
    assert payload["version"] == __version__
    assert payload["name"] == APP_TITLE
