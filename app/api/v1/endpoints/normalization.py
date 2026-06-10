"""API endpoint for skill normalization."""

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.normalization.schemas.schemas import NormalizationResult
from app.normalization.services.normalization_service import SkillNormalizationService

router = APIRouter()
normalization_service = SkillNormalizationService()


class NormalizationRequest(BaseModel):
    """Input contract for skill normalization request."""

    skills: list[str] = Field(
        ...,
        description="List of raw extracted skill terms to normalize",
        json_schema_extra={"example": ["ReactJS", "Python", "Postgres"]},
    )


@router.post(
    "/skills",
    response_model=NormalizationResult,
    status_code=status.HTTP_200_OK,
    summary="Normalize raw skills to canonical ESCO concepts",
    description="Maps a list of raw extracted skill terms to standard ESCO skill terms using multi-matcher ranking.",
)
async def normalize_skills(payload: NormalizationRequest) -> NormalizationResult:
    """Normalize a list of raw skill strings."""
    return normalization_service.normalize(payload.skills)
