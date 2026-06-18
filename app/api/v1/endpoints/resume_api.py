"""FastAPI router endpoint for Resume Intelligence."""

import os
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.logging.logger import get_logger
from app.resume.schemas.schemas import ResumeIntelligenceReport
from app.resume.services.service import ResumeService

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/analyze",
    response_model=ResumeIntelligenceReport,
    status_code=status.HTTP_200_OK,
    summary="Analyze an uploaded resume PDF file",
    description="Uploads a resume PDF file from the browser, parses its contents, and extracts structured resume intelligence.",
)
async def analyze_resume(
    file: UploadFile = File(...),  # noqa: B008
) -> ResumeIntelligenceReport:
    """Analyze an uploaded resume PDF and return structured intelligence."""
    logger.info("Received resume upload request", filename=file.filename)

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        logger.warning("Rejected upload: file is not a PDF", filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    # Save uploaded file
    upload_dir = os.path.join(os.getcwd(), "uploads", "resumes")
    os.makedirs(upload_dir, exist_ok=True)

    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}.pdf")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info("Saved uploaded resume PDF", file_path=file_path)
    except Exception as e:
        logger.error("Failed to save uploaded resume file", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}",
        ) from e

    try:
        service = ResumeService()
        report = await service.analyze_resume(file_path)
        return report
    except Exception as e:
        logger.error("Error analyzing resume", file_path=file_path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}",
        ) from e
    finally:
        # Clean up the uploaded file to prevent disk fill-up
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Cleaned up temporary resume PDF", file_path=file_path)
            except Exception as ex:
                logger.warning(
                    "Failed to remove temporary resume file",
                    file_path=file_path,
                    error=str(ex),
                )
