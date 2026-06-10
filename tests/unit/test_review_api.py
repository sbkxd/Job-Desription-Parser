"""Unit tests for Phase 6 Review API Endpoints."""

import json
import uuid
from datetime import datetime
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app.database.session import get_db_session
from app.main import app
from app.models.models import ReviewQueue, ReviewStatus
from app.review.schemas.schemas import ReviewResult, ReviewStatusSchema

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    mock_session = mock.AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: mock_session
    yield mock_session
    app.dependency_overrides.clear()


def test_list_reviews_endpoint_success(mock_db_session) -> None:
    review_id = uuid.uuid4()
    job_id = uuid.uuid4()
    flagged_reasons = json.dumps(
        {
            "skills": [
                {
                    "raw_skill": "Spring",
                    "normalized_skill": "Spring Framework",
                    "esco_id": "esco_spring",
                    "confidence": 0.72,
                    "reason": "REVIEW_REQUIRED",
                    "status": "pending",
                }
            ]
        }
    )
    mock_item = ReviewQueue(
        id=review_id,
        job_id=job_id,
        status=ReviewStatus.PENDING,
        flagged_reasons=flagged_reasons,
        created_at=datetime.utcnow(),
    )

    # Mock execute return list
    mock_execute_res = mock.MagicMock()
    mock_execute_res.scalars.return_value.all.return_value = [mock_item]
    mock_db_session.execute.return_value = mock_execute_res

    response = client.get("/api/v1/reviews")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(review_id)
    assert data[0]["status"] == "pending"


def test_get_review_by_id_endpoint_success(mock_db_session) -> None:
    review_id = uuid.uuid4()
    job_id = uuid.uuid4()
    flagged_reasons = json.dumps(
        {
            "skills": [
                {
                    "raw_skill": "Spring",
                    "normalized_skill": "Spring Framework",
                    "esco_id": "esco_spring",
                    "confidence": 0.72,
                    "reason": "REVIEW_REQUIRED",
                    "status": "pending",
                }
            ]
        }
    )
    mock_item = ReviewQueue(
        id=review_id,
        job_id=job_id,
        status=ReviewStatus.PENDING,
        flagged_reasons=flagged_reasons,
        created_at=datetime.utcnow(),
    )

    mock_db_session.get.return_value = mock_item

    response = client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(review_id)
    assert data["status"] == "pending"


def test_approve_review_skill_endpoint(mock_db_session) -> None:
    review_id = uuid.uuid4()
    mock_result = ReviewResult(
        id=review_id,
        status=ReviewStatusSchema.APPROVED,
        msg="Decision 'approve' processed successfully.",
        raw_skill="Spring",
        normalized_skill="Spring Framework",
        esco_id="esco_spring",
        confidence=0.72,
    )

    with mock.patch(
        "app.review.services.review_service.ReviewService.submit_decision",
        mock.AsyncMock(return_value=mock_result),
    ):
        response = client.post(
            f"/api/v1/reviews/{review_id}/approve",
            params={"raw_skill": "Spring", "reviewer": "admin"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["raw_skill"] == "Spring"


def test_reject_review_skill_endpoint(mock_db_session) -> None:
    review_id = uuid.uuid4()
    mock_result = ReviewResult(
        id=review_id,
        status=ReviewStatusSchema.REJECTED,
        msg="Decision 'reject' processed successfully.",
        raw_skill="Spring",
        normalized_skill=None,
        esco_id=None,
        confidence=0.0,
    )

    with mock.patch(
        "app.review.services.review_service.ReviewService.submit_decision",
        mock.AsyncMock(return_value=mock_result),
    ):
        response = client.post(
            f"/api/v1/reviews/{review_id}/reject",
            params={"raw_skill": "Spring", "reviewer": "admin"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["raw_skill"] == "Spring"


def test_correct_review_skill_endpoint(mock_db_session) -> None:
    review_id = uuid.uuid4()
    mock_result = ReviewResult(
        id=review_id,
        status=ReviewStatusSchema.CORRECTED,
        msg="Decision 'correct' processed successfully.",
        raw_skill="Spring",
        normalized_skill="Java Spring",
        esco_id="esco_java_spring",
        confidence=0.72,
    )

    with mock.patch(
        "app.review.services.review_service.ReviewService.submit_decision",
        mock.AsyncMock(return_value=mock_result),
    ):
        response = client.post(
            f"/api/v1/reviews/{review_id}/correct",
            params={
                "raw_skill": "Spring",
                "corrected_skill": "Java Spring",
                "esco_id": "esco_java_spring",
                "reviewer": "admin",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "corrected"
        assert data["normalized_skill"] == "Java Spring"
