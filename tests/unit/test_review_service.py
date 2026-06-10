"""Unit tests for ReviewService queue orchestration and decision logic."""

import json
import uuid
from unittest import mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Job, JobSkill, JobStatus, ReviewQueue, ReviewStatus, Skill
from app.normalization.schemas.schemas import NormalizedSkill
from app.review.schemas.schemas import ReviewDecision, ReviewStatusSchema
from app.review.services.review_service import ReviewService


@pytest.mark.asyncio
async def test_evaluate_and_flag_job_requires_review() -> None:
    mock_session = mock.AsyncMock(spec=AsyncSession)

    job_id = uuid.uuid4()
    mock_job = Job(id=job_id, status=JobStatus.PENDING, review_required=False)

    # Mock DB query results
    mock_result = mock.MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_job
    mock_session.execute.return_value = mock_result

    service = ReviewService(mock_session)
    service.queue_manager.get_by_job_id = mock.AsyncMock(return_value=None)

    # Out-of-taxonomy and low-confidence skills
    normalized_skills = [
        NormalizedSkill(
            raw_skill="LangChain",
            normalized_skill="LangChain",
            esco_id="unmapped",
            confidence=0.0,
            match_method="none",
        ),
        NormalizedSkill(
            raw_skill="Python",
            normalized_skill="Python",
            esco_id="esco_python",
            confidence=1.0,
            match_method="exact",
        ),
    ]

    flagged = await service.evaluate_and_flag_job(job_id, normalized_skills)

    assert flagged is True
    assert mock_job.review_required is True
    assert mock_job.status == JobStatus.REVIEW_REQUIRED
    # Check that an entry was added to the review queue
    mock_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_evaluate_and_flag_job_auto_approved() -> None:
    mock_session = mock.AsyncMock(spec=AsyncSession)

    job_id = uuid.uuid4()
    mock_job = Job(id=job_id, status=JobStatus.PENDING, review_required=False)

    mock_result = mock.MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_job
    mock_session.execute.return_value = mock_result

    service = ReviewService(mock_session)
    service.queue_manager.get_by_job_id = mock.AsyncMock(return_value=None)

    normalized_skills = [
        NormalizedSkill(
            raw_skill="Python",
            normalized_skill="Python",
            esco_id="esco_python",
            confidence=1.0,
            match_method="exact",
        )
    ]

    flagged = await service.evaluate_and_flag_job(job_id, normalized_skills)

    assert flagged is False
    assert mock_job.review_required is False
    assert mock_job.status == JobStatus.COMPLETED


@pytest.mark.asyncio
async def test_submit_approve_decision() -> None:
    mock_session = mock.AsyncMock(spec=AsyncSession)

    review_id = uuid.uuid4()
    job_id = uuid.uuid4()
    flagged_reasons = json.dumps(
        {
            "skills": [
                {
                    "raw_skill": "LangChain",
                    "normalized_skill": "LangChain",
                    "esco_id": "unmapped",
                    "confidence": 0.0,
                    "match_method": "none",
                    "status": "pending",
                }
            ]
        }
    )
    review_item = ReviewQueue(
        id=review_id,
        job_id=job_id,
        status=ReviewStatus.PENDING,
        flagged_reasons=flagged_reasons,
    )

    # Mock Repository lookup inside queue manager and DB session lookup
    mock_session.get.return_value = review_item

    # Mock JobSkill lookup in Decision service
    mock_job_skill = mock.MagicMock(spec=JobSkill)
    mock_job_skill_result = mock.MagicMock()
    mock_job_skill_result.scalars.return_value.first.return_value = mock_job_skill
    mock_session.execute.return_value = mock_job_skill_result

    service = ReviewService(mock_session)
    decision = ReviewDecision(
        action="approve",
        raw_skill="LangChain",
        reviewer="test_admin",
    )
    res = await service.submit_decision(review_id, decision)

    assert res is not None
    assert res.status == ReviewStatusSchema.APPROVED
    assert review_item.status == ReviewStatus.APPROVED
    assert review_item.reviewed_by == "test_admin"


@pytest.mark.asyncio
async def test_submit_correct_decision() -> None:
    mock_session = mock.AsyncMock(spec=AsyncSession)

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
                    "match_method": "embedding",
                    "status": "pending",
                }
            ]
        }
    )
    review_item = ReviewQueue(
        id=review_id,
        job_id=job_id,
        status=ReviewStatus.PENDING,
        flagged_reasons=flagged_reasons,
    )

    mock_session.get.return_value = review_item

    # Mock JobSkill lookup
    mock_job_skill = mock.MagicMock(spec=JobSkill)

    # Mock Skill lookup for corrected skill
    mock_skill = mock.MagicMock(spec=Skill)

    # Mock sequence of executes
    mock_res_job_skill = mock.MagicMock()
    mock_res_job_skill.scalars.return_value.first.return_value = mock_job_skill

    mock_res_skill = mock.MagicMock()
    mock_res_skill.scalars.return_value.first.return_value = mock_skill

    # Mock Job lookup for final job status update
    mock_job = Job(id=job_id, status=JobStatus.REVIEW_REQUIRED, review_required=True)
    mock_res_job = mock.MagicMock()
    mock_res_job.scalars.return_value.first.return_value = mock_job

    # When executing statements, return job_skill first, then skill, then job
    mock_session.execute.side_effect = [
        mock_res_job_skill,
        mock_res_skill,
        mock_res_job,
    ]

    service = ReviewService(mock_session)
    decision = ReviewDecision(
        action="correct",
        raw_skill="Spring",
        corrected_skill="Java Spring",
        esco_id="esco_java_spring",
        reviewer="test_admin",
    )
    res = await service.submit_decision(review_id, decision)

    assert res is not None
    assert res.status == ReviewStatusSchema.CORRECTED
    assert review_item.status == ReviewStatus.CORRECTED
