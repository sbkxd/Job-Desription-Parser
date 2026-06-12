"""LangGraph node for persisting all parsed job, skill, and review data to the database."""

import time
import uuid
from typing import Any, Dict

from sqlalchemy import select

from app.models.models import (
    Job,
    JobSkill,
    JobStatus,
    RequirementType,
    ReviewQueue,
    ReviewStatus,
    Skill,
)
from app.orchestration.state.state import PipelineState


async def persistence_node(state: PipelineState) -> Dict[str, Any]:
    """Persist job, skills, job_skills, and review queue items to database.

    Args:
        state: The current PipelineState.

    Returns:
        State updates containing persistence_result, errors, and execution_metadata.
    """
    start_time = time.perf_counter()
    db = state.get("db")
    errors = []
    persistence_result = {}

    if not db:
        return {
            "errors": [
                "Database session 'db' is missing in state. Persistence skipped."
            ],
            "execution_metadata": {
                "persistence_duration_ms": 0.0,
                "node_persist_success": False,
            },
        }

    try:
        source = state.get("job_source") or {}
        raw_doc = state.get("raw_document") or ""
        extracted = state.get("extraction_result") or {}
        normalized = state.get("normalization_result") or {}
        review_res = state.get("review_result") or {}

        # 1. Prepare Job UUID (re-use from state if set, else generate)
        job_id = source.get("job_id")
        if not job_id:
            job_id = uuid.uuid4()
        else:
            if isinstance(job_id, str):
                job_id = uuid.UUID(job_id)

        # Map experience ranges
        exp = extracted.get("experience") or {}
        exp_min = exp.get("min_years")
        exp_max = exp.get("max_years")

        # Map job status
        needs_review = review_res.get("needs_review", False)
        job_status = JobStatus.REVIEW_REQUIRED if needs_review else JobStatus.COMPLETED

        # Create/insert Job record
        job = Job(
            id=job_id,
            title=source.get("title") or "Unknown Title",
            company=source.get("company"),
            location=source.get("location"),
            seniority=extracted.get("seniority"),
            source_url=source.get("url"),
            raw_text=raw_doc,
            status=job_status,
            review_required=needs_review,
            experience_min=float(exp_min) if exp_min is not None else None,
            experience_max=float(exp_max) if exp_max is not None else None,
            confidence_score=1.0 if not needs_review else 0.8,
        )
        await db.merge(job)
        await db.flush()

        # 2. Persist Skills and JobSkill links
        skills = normalized.get("skills") or []
        skill_ids = []

        for s in skills:
            skill_name = s.get("raw_skill") or s.get("normalized_skill")
            if not skill_name:
                continue

            # Check if skill exists
            stmt = select(Skill).where(Skill.name.ilike(skill_name))
            res = await db.execute(stmt)
            skill_record = res.scalars().first()

            if not skill_record:
                skill_record = Skill(
                    id=uuid.uuid4(),
                    name=skill_name,
                    normalized_name=s.get("normalized_skill"),
                    esco_code=s.get("esco_id"),
                    category="Extracted Skill",
                )
                db.add(skill_record)
                await db.flush()

            skill_ids.append(str(skill_record.id))

            # Create JobSkill association link
            job_skill = JobSkill(
                id=uuid.uuid4(),
                job_id=job_id,
                skill_id=skill_record.id,
                requirement_type=RequirementType.MUST_HAVE,
                confidence_score=s.get("confidence", 1.0),
            )
            db.add(job_skill)

        # 3. Create ReviewQueue record if review is required
        if needs_review:
            flagged_reasons = review_res.get("flagged_reasons")
            review_queue = ReviewQueue(
                id=uuid.uuid4(),
                job_id=job_id,
                status=ReviewStatus.PENDING,
                flagged_reasons=flagged_reasons,
            )
            db.add(review_queue)

        await db.flush()
        persistence_result = {
            "job_id": str(job_id),
            "skill_ids": skill_ids,
        }

    except Exception as e:
        errors.append(f"Persistence failed: {str(e)}")

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "persistence_result": persistence_result,
        "errors": errors,
        "execution_metadata": {
            "persistence_duration_ms": duration_ms,
            "node_persist_success": len(errors) == 0,
        },
    }
