"""Orchestration service for reviewing skill mappings, queue management, and audit tracking."""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Job, JobStatus, ReviewQueue, ReviewStatus
from app.normalization.schemas.schemas import NormalizedSkill
from app.review.audit.audit_trail import AuditTrailSystem
from app.review.decisions.decision_engine import ReviewDecisionService
from app.review.evaluators.confidence_evaluator import ConfidenceEvaluator
from app.review.evaluators.out_of_taxonomy import OutOfTaxonomyDetector
from app.review.queues.queue_manager import ReviewQueueManager
from app.review.schemas.schemas import ReviewDecision, ReviewResult, ReviewStatusSchema


class ReviewService:
    """Orchestrates confidence evaluation, queue insertion, decisions, and auditing."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.confidence_evaluator = ConfidenceEvaluator()
        self.out_of_taxonomy_detector = OutOfTaxonomyDetector()
        self.queue_manager = ReviewQueueManager(session)
        self.decision_service = ReviewDecisionService(session)
        self.audit_trail = AuditTrailSystem(session)

    async def evaluate_and_flag_job(
        self, job_id: UUID, normalized_skills: list[NormalizedSkill]
    ) -> bool:
        """Evaluate normalized skills and flag the job for review if needed.

        Args:
            job_id: The ID of the Job.
            normalized_skills: List of normalized skills from normalization service.

        Returns:
            True if job was flagged for review, False otherwise.
        """
        # Find the job
        res = await self.session.execute(select(Job).where(Job.id == job_id))
        job = res.scalars().first()
        if not job:
            return False

        flagged_skills = []
        for norm_skill in normalized_skills:
            # 1. Out of taxonomy check
            oot_res = self.out_of_taxonomy_detector.detect(
                norm_skill.raw_skill, norm_skill.esco_id
            )

            # 2. Confidence threshold evaluation
            status, reason = self.confidence_evaluator.evaluate(
                norm_skill.confidence, norm_skill.match_method
            )

            if oot_res["review_required"] or status == ReviewStatusSchema.PENDING:
                # Add to queue candidate list
                flagged_skills.append(
                    {
                        "raw_skill": norm_skill.raw_skill,
                        "normalized_skill": norm_skill.normalized_skill,
                        "esco_id": norm_skill.esco_id,
                        "confidence": norm_skill.confidence,
                        "match_method": norm_skill.match_method,
                        "status": "pending",
                        "reason": (
                            "OUT_OF_TAXONOMY" if oot_res["review_required"] else reason
                        ),
                    }
                )

        if flagged_skills:
            # Job requires review
            job.review_required = True
            job.status = JobStatus.REVIEW_REQUIRED

            # Check if review queue item already exists
            review_item = await self.queue_manager.get_by_job_id(job_id)
            flagged_reasons_str = json.dumps({"skills": flagged_skills})

            if review_item:
                review_item.status = ReviewStatus.PENDING
                review_item.flagged_reasons = flagged_reasons_str
            else:
                review_item = ReviewQueue(
                    job_id=job_id,
                    status=ReviewStatus.PENDING,
                    flagged_reasons=flagged_reasons_str,
                )
                await self.queue_manager.add(review_item)

            await self.session.flush()
            return True

        # Auto-approved / complete
        job.review_required = False
        job.status = JobStatus.COMPLETED
        await self.session.flush()
        return False

    async def _process_action(
        self,
        job_id: UUID,
        action: str,
        decision: ReviewDecision,
        target_skill: dict[str, Any],
    ) -> bool:
        """Route the review action to decision service and update target skill properties."""
        if action == "approve":
            success = await self.decision_service.approve_skill(
                job_id, decision.raw_skill, decision.reviewer
            )
            target_skill["status"] = "approved"
            return success
        elif action == "reject":
            success = await self.decision_service.reject_skill(
                job_id, decision.raw_skill, decision.reviewer
            )
            target_skill["status"] = "rejected"
            return success
        elif action == "correct":
            if not decision.corrected_skill:
                return False
            success = await self.decision_service.correct_skill(
                job_id,
                decision.raw_skill,
                decision.corrected_skill,
                decision.esco_id,
                decision.reviewer,
            )
            target_skill["status"] = "corrected"
            target_skill["normalized_skill"] = decision.corrected_skill
            target_skill["esco_id"] = decision.esco_id or "custom_override"
            return success
        return False

    async def _update_review_status(
        self,
        review_item: ReviewQueue,
        skills_list: list[dict[str, Any]],
        action: str,
        reviewer: str | None,
    ) -> None:
        """Check if all skills in review item are resolved and update status accordingly."""
        all_resolved = all(skill["status"] != "pending" for skill in skills_list)
        if all_resolved:
            review_item.status = (
                ReviewStatus.APPROVED if action == "approve" else ReviewStatus.REJECTED
            )
            if any(s["status"] == "corrected" for s in skills_list):
                review_item.status = ReviewStatus.CORRECTED

            review_item.reviewed_at = datetime.utcnow()
            review_item.reviewed_by = reviewer

            # Update job status
            res = await self.session.execute(
                select(Job).where(Job.id == review_item.job_id)
            )
            job = res.scalars().first()
            if job:
                job.review_required = False
                job.status = JobStatus.COMPLETED

    async def submit_decision(
        self, review_id: UUID, decision: ReviewDecision
    ) -> ReviewResult | None:
        """Submit a reviewer decision on a specific flagged skill.

        Args:
            review_id: ID of the ReviewQueue record.
            decision: ReviewDecision payload containing action details.

        Returns:
            ReviewResult details or None.
        """
        review_item = await self.queue_manager.get(review_id)
        if not review_item:
            return None

        # Load current flagged reasons JSON structure
        flagged_data = json.loads(review_item.flagged_reasons or '{"skills": []}')
        skills_list = flagged_data.get("skills", [])

        # Find the target skill being reviewed
        target_skill = None
        for skill in skills_list:
            if skill["raw_skill"].lower() == decision.raw_skill.lower():
                target_skill = skill
                break

        if not target_skill:
            return None

        job_id = review_item.job_id
        action = decision.action.lower()

        success = await self._process_action(job_id, action, decision, target_skill)
        if not success:
            return None

        # Write audit log record
        await self.audit_trail.record_action(
            job_id=job_id,
            action=f"skill_{action}",
            actor=decision.reviewer,
            raw_skill=decision.raw_skill,
            normalized_skill=target_skill["normalized_skill"],
            decision=action.upper(),
            confidence=target_skill["confidence"],
        )

        await self._update_review_status(
            review_item, skills_list, action, decision.reviewer
        )

        # Save changes to flagged reasons JSON structure
        review_item.flagged_reasons = json.dumps({"skills": skills_list})
        await self.session.flush()

        schema_status = ReviewStatusSchema(review_item.status.value)
        return ReviewResult(
            id=review_item.id,
            status=schema_status,
            msg=f"Decision '{action}' processed successfully.",
            raw_skill=decision.raw_skill,
            normalized_skill=target_skill["normalized_skill"],
            esco_id=target_skill["esco_id"],
            confidence=target_skill["confidence"],
        )
