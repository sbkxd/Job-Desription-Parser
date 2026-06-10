"""Preprocessing endpoint — segments job description text into sections."""

from fastapi import APIRouter, HTTPException, status

from app.preprocessing.schemas.schemas import RawDocument, SegmentationResult
from app.preprocessing.services.segmentation_service import SegmentationService

router = APIRouter()
segmentation_service = SegmentationService()


@router.post(
    "/segment",
    response_model=SegmentationResult,
    status_code=status.HTTP_200_OK,
    summary="Segment job description text",
    description="Cleans and segments job description text into structured, typed sections.",
)
async def segment_job_description(document: RawDocument) -> SegmentationResult:
    """Preprocess and segment a job description document."""
    result = segmentation_service.segment(document)
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result.error or "Unknown segmentation error",
        )
    return result
