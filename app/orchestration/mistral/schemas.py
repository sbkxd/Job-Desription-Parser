"""Schemas for Mistral Structured Responses and Auditing Metrics."""

from typing import Optional

from pydantic import BaseModel, Field


class AmbiguousSkillSchema(BaseModel):
    """Schema for resolving ambiguous taxonomy matches."""

    selected_skill: Optional[str] = Field(
        default=None,
        description="The selected canonical candidate match from the provided list, or null if none fit.",
    )
    reason: str = Field(
        description="Reasoning process for selecting or rejecting the candidates based on context."
    )


class ReviewAssistanceSchema(BaseModel):
    """Schema for out-of-taxonomy review support."""

    category: str = Field(
        description="The suggested category/grouping for this new out-of-taxonomy skill."
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0 representing the quality of the classification."
    )


class MistralInvocationAudit(BaseModel):
    """Audit metrics for tracking every Mistral API invocation."""

    prompt_version: str
    model_version: str
    request_timestamp: str
    response_timestamp: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    status: str  # success, failed
    error_message: Optional[str] = None
