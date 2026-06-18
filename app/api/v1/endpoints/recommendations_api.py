"""FastAPI router endpoints for Resume Recommendations & Optimization."""

from fastapi import APIRouter, HTTPException, status

from app.api.v1.endpoints.compatibility_api import DirectCompatibilityRequest
from app.logging.logger import get_logger
from app.recommendations.schemas.schemas import ResumeOptimizationReport
from app.recommendations.services.service import RecommendationService

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/recommendations",
    response_model=ResumeOptimizationReport,
    status_code=status.HTTP_200_OK,
    summary="Generate personalized resume optimization recommendations",
    description="Analyzes Job & Resume profiles and uses Mistral LLM to generate ATS and section-level recommendations.",
)
async def generate_recommendations(
    payload: DirectCompatibilityRequest,
) -> ResumeOptimizationReport:
    """Generate resume optimization recommendations and ATS keyword suggestions."""
    logger.info("Received resume recommendations request")
    service = RecommendationService()
    try:
        report = await service.generate_recommendations(payload.resume, payload.job)
        return report
    except Exception as e:
        logger.error("Resume recommendations endpoint failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendations generation failed: {str(e)}",
        ) from e
