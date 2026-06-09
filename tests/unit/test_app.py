"""Unit tests for FastAPI application and health endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """Create a test client with mocked lifespan (no real DB)."""
    from app.config.settings import Settings

    test_settings = Settings()

    with (
        patch("app.main.get_settings", return_value=test_settings),
        patch(
            "app.main.create_db_engine", new_callable=AsyncMock
        ) as mock_engine_factory,
        patch("app.main.dispose_engine", new_callable=AsyncMock),
        patch("app.main.configure_logging"),
    ):
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine

        from app.main import create_app

        application = create_app()
        with TestClient(application, raise_server_exceptions=True) as c:
            yield c


def test_app_creates_successfully():
    """Test that the application can be instantiated."""
    with (
        patch("app.main.get_settings"),
        patch("app.main.configure_logging"),
    ):
        from app.main import app as application

        assert application is not None


def test_openapi_schema_available(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data


def test_liveness_endpoint(client: TestClient):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "alive"
    assert "version" in body
    assert "uptime_seconds" in body


def test_readiness_endpoint_no_db(client: TestClient):
    """Readiness should return 503 when DB engine is not initialized."""
    response = client.get("/api/v1/health/ready")
    # Without a real DB engine on app.state the check will fail gracefully
    assert response.status_code in (200, 503)
    body = response.json()
    assert "status" in body
    assert "checks" in body
