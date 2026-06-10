"""Unit tests for the Skill Normalization API router."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_normalize_skills_endpoint_success() -> None:
    payload = {"skills": ["ReactJS", "python", "UnknownSkill"]}
    response = client.post("/api/v1/normalize/skills", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "normalized_skills" in data
    normalized_list = data["normalized_skills"]
    assert len(normalized_list) == 3

    # ReactJS match check
    react_match = next(s for s in normalized_list if s["raw_skill"] == "ReactJS")
    assert react_match["normalized_skill"] == "React"
    assert react_match["esco_id"] == "esco_react"
    assert react_match["match_method"] == "alias"
    assert react_match["confidence"] == 0.95

    # python match check
    python_match = next(s for s in normalized_list if s["raw_skill"] == "python")
    assert python_match["normalized_skill"] == "Python"
    assert python_match["esco_id"] == "esco_python"
    assert python_match["match_method"] == "exact"
    assert python_match["confidence"] == 1.0


def test_normalize_skills_endpoint_empty_list() -> None:
    payload = {"skills": []}
    response = client.post("/api/v1/normalize/skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["normalized_skills"] == []


def test_normalize_skills_endpoint_invalid_payload() -> None:
    # Missing required 'skills' field
    payload = {}
    response = client.post("/api/v1/normalize/skills", json=payload)
    assert response.status_code == 422
