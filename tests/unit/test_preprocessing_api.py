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


def test_preprocess_segment_api_success(client: TestClient):
    payload = {
        "raw_text": "About Altrosyn:\nWe are a startup.\n\nKey Responsibilities:\n- Write Python code.",
        "source_type": "greenhouse",
        "source_url": "http://example.com/jd",
    }
    response = client.post("/api/v1/preprocess/segment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["document"] is not None
    assert data["duration_ms"] is not None

    doc = data["document"]
    assert len(doc["sections"]) == 2
    # Verify section contents
    sec_types = [s["section_type"] for s in doc["sections"]]
    assert "about_company" in sec_types
    assert "responsibilities" in sec_types


def test_preprocess_segment_api_validation_error(client: TestClient):
    # Empty raw_text should fail validation
    payload = {
        "raw_text": "   ",
    }
    response = client.post("/api/v1/preprocess/segment", json=payload)
    assert response.status_code == 422
