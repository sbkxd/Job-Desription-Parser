"""FastAPI endpoints for managing the human review queue and decisions."""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.models.models import ReviewQueue
from app.review.schemas.schemas import (
    ReviewDecision,
    ReviewItem,
    ReviewResult,
    ReviewStatusSchema,
)
from app.review.services.review_service import ReviewService

router = APIRouter()


@router.get("", response_model=list[ReviewItem])
async def list_reviews(
    status: ReviewStatusSchema | None = None,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> list[ReviewItem]:
    """Retrieve a list of review queue items, optionally filtered by status."""
    stmt = select(ReviewQueue)
    if status is not None:
        stmt = stmt.where(ReviewQueue.status == status.value)
    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    queue_items = result.scalars().all()

    items = []
    for rq in queue_items:
        try:
            data = json.loads(rq.flagged_reasons) if rq.flagged_reasons else {}
            skills = data.get("skills", [])
        except Exception:
            skills = []
        for skill in skills:
            items.append(
                ReviewItem(
                    id=rq.id,
                    job_id=rq.job_id,
                    raw_skill=skill.get("raw_skill", ""),
                    normalized_skill=skill.get("normalized_skill"),
                    esco_id=skill.get("esco_id"),
                    confidence=skill.get("confidence", 0.0),
                    review_reason=skill.get("reason", "unknown"),
                    status=ReviewStatusSchema(rq.status.value),
                    flagged_reasons=rq.flagged_reasons,
                    created_at=rq.created_at,
                    reviewed_at=rq.reviewed_at,
                    reviewed_by=rq.reviewed_by,
                )
            )
    return items


@router.get("/{id}", response_model=ReviewItem)
async def get_review(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> ReviewItem:
    """Retrieve details for a specific review queue entry."""
    review_item = await db.get(ReviewQueue, id)
    if not review_item:
        raise HTTPException(status_code=404, detail="Review item not found.")
    try:
        data = (
            json.loads(review_item.flagged_reasons)
            if review_item.flagged_reasons
            else {}
        )
        skills = data.get("skills", [])
    except Exception:
        skills = []

    first_skill = skills[0] if skills else {}
    return ReviewItem(
        id=review_item.id,
        job_id=review_item.job_id,
        raw_skill=first_skill.get("raw_skill", "unknown"),
        normalized_skill=first_skill.get("normalized_skill"),
        esco_id=first_skill.get("esco_id"),
        confidence=first_skill.get("confidence", 0.0),
        review_reason=first_skill.get("reason", "unknown"),
        status=ReviewStatusSchema(review_item.status.value),
        flagged_reasons=review_item.flagged_reasons,
        created_at=review_item.created_at,
        reviewed_at=review_item.reviewed_at,
        reviewed_by=review_item.reviewed_by,
    )


@router.post("/{id}/approve", response_model=ReviewResult)
async def approve_review_item(
    id: UUID,
    raw_skill: str = Query(..., description="The raw skill name to approve."),
    reviewer: str | None = Query(default=None, description="The reviewer name."),
    db: AsyncSession = Depends(get_db_session),
) -> ReviewResult:
    """Approve a suggested skill mapping for a job."""
    service = ReviewService(db)
    decision = ReviewDecision(
        action="approve",
        raw_skill=raw_skill,
        reviewer=reviewer,
    )
    result = await service.submit_decision(id, decision)
    if not result:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to process approval for skill '{raw_skill}'.",
        )
    return result


@router.post("/{id}/reject", response_model=ReviewResult)
async def reject_review_item(
    id: UUID,
    raw_skill: str = Query(..., description="The raw skill name to reject."),
    reviewer: str | None = Query(default=None, description="The reviewer name."),
    db: AsyncSession = Depends(get_db_session),
) -> ReviewResult:
    """Reject and remove a skill mapping suggestion."""
    service = ReviewService(db)
    decision = ReviewDecision(
        action="reject",
        raw_skill=raw_skill,
        reviewer=reviewer,
    )
    result = await service.submit_decision(id, decision)
    if not result:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to process rejection for skill '{raw_skill}'.",
        )
    return result


@router.post("/{id}/correct", response_model=ReviewResult)
async def correct_review_item(
    id: UUID,
    raw_skill: str = Query(..., description="The raw skill name to correct."),
    corrected_skill: str = Query(
        ..., description="The corrected skill name replacement."
    ),
    esco_id: str | None = Query(default=None, description="The corrected ESCO ID."),
    reviewer: str | None = Query(default=None, description="The reviewer name."),
    db: AsyncSession = Depends(get_db_session),
) -> ReviewResult:
    """Correct and override a skill mapping with a new value."""
    service = ReviewService(db)
    decision = ReviewDecision(
        action="correct",
        raw_skill=raw_skill,
        corrected_skill=corrected_skill,
        esco_id=esco_id,
        reviewer=reviewer,
    )
    result = await service.submit_decision(id, decision)
    if not result:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to process correction for skill '{raw_skill}'.",
        )
    return result
