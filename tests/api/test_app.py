from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import create_app


def test_health_endpoint(isolated_settings) -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
