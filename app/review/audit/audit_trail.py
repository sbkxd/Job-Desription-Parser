"""Audit trail system for Phase 6 review actions."""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuditLog


class AuditTrailSystem:
    """Records review queue actions in database audit logs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_action(
        self,
        job_id: UUID,
        action: str,
        actor: str | None,
        raw_skill: str,
        normalized_skill: str | None,
        decision: str,
        confidence: float,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Create and persist an audit log entry for a review decision."""
        # Standardize audit details payload
        details_payload = {
            "original_skill": raw_skill,
            "normalized_skill": normalized_skill,
            "reviewer_decision": decision,
            "confidence_score": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {}),
        }

        audit_entry = AuditLog(
            job_id=job_id,
            action=action,
            actor=actor or "reviewer",
            details=json.dumps(details_payload),
        )

        self.session.add(audit_entry)
        await self.session.flush()
        return audit_entry
