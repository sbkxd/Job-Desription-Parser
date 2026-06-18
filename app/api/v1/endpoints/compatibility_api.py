"""FastAPI router endpoints for Job ↔ Resume Compatibility Engine."""

import os
import shutil
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.compatibility.schemas.schemas import CompatibilityReport
from app.compatibility.services.service import CompatibilityService
from app.database.session import get_db_session
from app.logging.logger import get_logger
from app.presentation.schemas.job_intelligence import JobIntelligenceReport
from app.resume.schemas.schemas import ResumeIntelligenceReport

logger = get_logger(__name__)
router = APIRouter()


# Since we need a JSON body structure, let's write a simple Pydantic helper


class DirectCompatibilityRequest(BaseModel):
    """Payload for comparing pre-parsed resume and job reports."""

    resume: ResumeIntelligenceReport
    job: JobIntelligenceReport


@router.post(
    "/analyze",
    response_model=CompatibilityReport,
    status_code=status.HTTP_200_OK,
    summary="Directly compare pre-parsed Resume and Job Intelligence Reports",
)
async def analyze_compatibility(
    payload: DirectCompatibilityRequest,
) -> CompatibilityReport:
    """Analyze compatibility between pre-parsed resume and job reports."""
    logger.info("Received direct compatibility analysis request")
    service = CompatibilityService()
    try:
        report = await service.analyze_compatibility(payload.resume, payload.job)
        return report
    except Exception as e:
        logger.error("Direct compatibility analysis endpoint failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compatibility analysis failed: {str(e)}",
        ) from e


@router.post(
    "/analyze-pdf",
    response_model=CompatibilityReport,
    status_code=status.HTTP_200_OK,
    summary="Compare an uploaded resume PDF against a Job ID or Job PDF",
)
async def analyze_compatibility_pdf(
    resume_file: UploadFile = File(...),  # noqa: B008
    job_id: Optional[str] = Form(None),
    job_file: Optional[UploadFile] = File(None),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),
) -> CompatibilityReport:
    """Compare a resume PDF upload against a database Job ID or another uploaded Job PDF."""
    logger.info(
        "Received compatibility PDF analysis request",
        resume_filename=resume_file.filename,
        job_id=job_id,
        job_file_provided=job_file is not None,
    )

    if not resume_file.filename or not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file must be a PDF.",
        )

    if not job_id and not job_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'job_id' or 'job_file' must be provided.",
        )

    # Save temp resume file
    upload_dir = os.path.join(os.getcwd(), "uploads", "compatibility")
    os.makedirs(upload_dir, exist_ok=True)

    resume_id = str(uuid.uuid4())
    resume_path = os.path.join(upload_dir, f"resume_{resume_id}.pdf")

    try:
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save resume file: {str(e)}",
        ) from e

    job_pdf_path = None
    try:
        service = CompatibilityService()

        # Case 1: Compare against an uploaded job PDF
        if job_file:
            if not job_file.filename or not job_file.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job file must be a PDF.",
                )
            job_pdf_id = str(uuid.uuid4())
            job_pdf_path = os.path.join(upload_dir, f"job_{job_pdf_id}.pdf")

            with open(job_pdf_path, "wb") as buffer:
                shutil.copyfileobj(job_file.file, buffer)

            report = await service.analyze_compatibility_by_job_pdf(
                resume_path, job_pdf_path, db
            )

        # Case 2: Compare against a Job ID from the DB
        else:
            assert job_id is not None
            report = await service.analyze_compatibility_by_job_id(
                resume_path, job_id, db
            )

        return report

    except Exception as e:
        logger.error("Compatibility PDF analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compatibility PDF analysis failed: {str(e)}",
        ) from e
    finally:
        # Cleanup
        if os.path.exists(resume_path):
            os.remove(resume_path)
        if job_pdf_path and os.path.exists(job_pdf_path):
            os.remove(job_pdf_path)


@router.post(
    "/analyze-url",
    response_model=CompatibilityReport,
    status_code=status.HTTP_200_OK,
    summary="Compare an uploaded resume PDF against a Job URL",
)
async def analyze_compatibility_url(
    resume_file: UploadFile = File(...),  # noqa: B008
    job_url: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
) -> CompatibilityReport:
    """Compare a resume PDF upload against a parsed Job URL."""
    logger.info(
        "Received compatibility URL analysis request",
        resume_filename=resume_file.filename,
        job_url=job_url,
    )

    if not resume_file.filename or not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file must be a PDF.",
        )

    # Save temp resume file
    upload_dir = os.path.join(os.getcwd(), "uploads", "compatibility")
    os.makedirs(upload_dir, exist_ok=True)

    resume_id = str(uuid.uuid4())
    resume_path = os.path.join(upload_dir, f"resume_{resume_id}.pdf")

    try:
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save resume file: {str(e)}",
        ) from e

    try:
        service = CompatibilityService()
        report = await service.analyze_compatibility_by_job_url(
            resume_path, job_url, db
        )
        return report
    except Exception as e:
        logger.error("Compatibility URL analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compatibility URL analysis failed: {str(e)}",
        ) from e
    finally:
        # Cleanup
        if os.path.exists(resume_path):
            os.remove(resume_path)
