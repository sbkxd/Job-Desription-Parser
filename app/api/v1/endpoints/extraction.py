"""Extraction API endpoint."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.extraction.schemas.schemas import ExtractionResult
from app.extraction.services.extraction_service import ExtractionService

router = APIRouter()
extraction_service = ExtractionService()


class ExtractionRequest(BaseModel):
    """Input contract wrapping the segmented document dictionary."""

    segmented_document: dict[str, list[str]] = Field(
        ...,
        description="Dictionary mapping SectionType keys to lines of text content",
        json_schema_extra={
            "example": {
                "responsibilities": ["Develop Python APIs.", "Maintain database."],
                "requirements": ["3+ years of experience.", "Strong SQL knowledge."],
                "nice_to_have": ["Experience with AWS preferred."],
            }
        },
    )


@router.post(
    "",
    response_model=ExtractionResult,
    status_code=status.HTTP_200_OK,
    summary="Extract structured information from job description sections",
    description="Extracts skills, experience range, seniority, and classifies requirements from segmented text.",
)
async def extract_information(payload: ExtractionRequest) -> ExtractionResult:
    """Run information extraction pipeline on a segmented job description."""
    result = extraction_service.extract(payload.segmented_document)
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result.error or "Unknown extraction error",
        )
    return result
