"""Pydantic schemas for review queue, decisions, and audit trails."""

import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewStatusSchema(str, enum.Enum):
    """Lifecycle states of a review item."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CORRECTED = "corrected"


class ReviewItem(BaseModel):
    """Represents a skill normalization entry requiring human review."""

    id: UUID = Field(description="Unique identifier for the review item.")
    job_id: UUID = Field(description="Associated job ID.")
    raw_skill: str = Field(description="The original raw skill mention.")
    normalized_skill: str | None = Field(
        default=None, description="The suggested normalized skill, if any."
    )
    esco_id: str | None = Field(
        default=None, description="The suggested ESCO ID, if any."
    )
    confidence: float = Field(description="Normalization confidence score.")
    review_reason: str = Field(description="Reason why review was flagged.")
    status: ReviewStatusSchema = Field(
        default=ReviewStatusSchema.PENDING, description="Current status of review."
    )
    flagged_reasons: str | None = Field(
        default=None, description="Detailed flagged reasons/context."
    )
    created_at: datetime = Field(description="Creation timestamp.")
    reviewed_at: datetime | None = Field(
        default=None, description="Timestamp when review completed."
    )
    reviewed_by: str | None = Field(
        default=None, description="Identifier of the reviewer."
    )

    model_config = ConfigDict(from_attributes=True)


class ReviewDecision(BaseModel):
    """Payload representing a human review decision."""

    action: str = Field(
        description="The action to perform: 'approve', 'reject', or 'correct'."
    )
    raw_skill: str = Field(description="The raw skill name being target reviewed.")
    corrected_skill: str | None = Field(
        default=None,
        description="Corrected/new mapping skill name (required for 'correct').",
    )
    esco_id: str | None = Field(
        default=None,
        description="Override ESCO ID (optional/required for 'correct').",
    )
    reviewer: str | None = Field(
        default=None, description="Identifier of the reviewer."
    )


class AuditRecord(BaseModel):
    """Audit trail record for a review action."""

    id: UUID
    job_id: UUID
    action: str
    actor: str | None
    details: str | None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewResult(BaseModel):
    """Outcome of processing a review item."""

    id: UUID
    status: ReviewStatusSchema
    msg: str
    raw_skill: str
    normalized_skill: str | None
    esco_id: str | None
    confidence: float
