"""FastAPI router endpoint for triggering the orchestrated parser pipeline."""

import os
import shutil
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.orchestration.schemas.schemas import PipelinePdfRequest, PipelineUrlRequest
from app.orchestration.services.pipeline_service import PipelineService
from app.presentation.formatters.response_builder import ResponseBuilder
from app.presentation.schemas.job_intelligence import JobIntelligenceReport

router = APIRouter()


@router.post(
    "/run/url",
    response_model=JobIntelligenceReport,
    status_code=status.HTTP_200_OK,
    summary="Run unified parser pipeline on a URL",
    description="Runs the unified LangGraph workflow (Ingestion -> Segmentation -> Extraction -> Normalization -> Review) on a web page URL.",
)
async def run_pipeline_url(
    payload: PipelineUrlRequest,
    db: AsyncSession = Depends(get_db_session),
) -> JobIntelligenceReport:
    """Execute the full job description parser pipeline on a URL."""
    service = PipelineService(db)
    final_state = await service.run_pipeline(url=payload.url)

    if final_state.get("errors") and not final_state.get("raw_document"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline execution failed: {', '.join(final_state['errors'])}",
        )

    return ResponseBuilder.build_report(final_state)


@router.post(
    "/run/pdf",
    response_model=JobIntelligenceReport,
    status_code=status.HTTP_200_OK,
    summary="Run unified parser pipeline on a PDF",
    description="Runs the unified LangGraph workflow (Ingestion -> Segmentation -> Extraction -> Normalization -> Review) on a local PDF file path.",
)
async def run_pipeline_pdf(
    payload: PipelinePdfRequest,
    db: AsyncSession = Depends(get_db_session),
) -> JobIntelligenceReport:
    """Execute the full job description parser pipeline on a local PDF path."""
    service = PipelineService(db)
    final_state = await service.run_pipeline(pdf_path=payload.pdf_path)

    if final_state.get("errors") and not final_state.get("raw_document"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline execution failed: {', '.join(final_state['errors'])}",
        )

    return ResponseBuilder.build_report(final_state)


@router.post(
    "/run/upload",
    response_model=JobIntelligenceReport,
    status_code=status.HTTP_200_OK,
    summary="Run unified parser pipeline on an uploaded PDF file",
    description="Uploads a PDF file from the browser, saves it locally, and executes the LangGraph pipeline on it.",
)
async def run_pipeline_upload(
    file: UploadFile = File(...),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),
) -> JobIntelligenceReport:
    """Execute the full job description parser pipeline on an uploaded PDF."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    # Save uploaded file
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    import uuid

    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}.pdf")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}",
        ) from e

    service = PipelineService(db)
    final_state = await service.run_pipeline(pdf_path=file_path)

    if final_state.get("errors") and not final_state.get("raw_document"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline execution failed: {', '.join(final_state['errors'])}",
        )

    return ResponseBuilder.build_report(final_state)


@router.get(
    "/debug/{job_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieve full internal pipeline execution state",
)
async def get_pipeline_debug(
    job_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve the full internal PipelineState for the latest run of a given job_id."""
    import uuid

    from sqlalchemy import select

    from app.models.models import ProcessingRun

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job_id UUID format",
        ) from None

    stmt = (
        select(ProcessingRun)
        .where(ProcessingRun.job_id == job_uuid)
        .order_by(ProcessingRun.started_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    run_record = result.scalars().first()

    if not run_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No processing run found for job_id {job_id}",
        )

    if not run_record.pipeline_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No internal pipeline state persisted for job_id {job_id}",
        )

    return run_record.pipeline_state
