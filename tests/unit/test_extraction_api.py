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


def test_extract_api_success(client: TestClient):
    payload = {
        "segmented_document": {
            "responsibilities": ["Develop APIs using Python."],
            "requirements": ["Must have 3 years of experience.", "FastAPI knowledge."],
            "nice_to_have": ["Docker preferred."],
        }
    }
    response = client.post("/api/v1/extract", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["skills"]) > 0
    assert data["experience"]["min_years"] == 3.0
    assert data["seniority"]["seniority"] == "Mid"  # fallback due to 3 years min_years
    assert len(data["requirements_classification"]) == 3


def test_extract_api_validation_error(client: TestClient):
    # Invalid request body (missing segmented_document)
    payload = {}
    response = client.post("/api/v1/extract", json=payload)
    assert response.status_code == 422
