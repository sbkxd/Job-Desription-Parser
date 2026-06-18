"""Service layer coordinating Job ↔ Resume Compatibility matching and scoring."""

import time
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.compatibility.schemas.schemas import CompatibilityReport
from app.compatibility.scoring.scoring import CompatibilityEngine
from app.logging.logger import get_logger
from app.models.models import ProcessingRun
from app.orchestration.services.pipeline_service import PipelineService
from app.presentation.formatters.response_builder import ResponseBuilder
from app.presentation.schemas.job_intelligence import JobIntelligenceReport
from app.resume.schemas.schemas import ResumeIntelligenceReport
from app.resume.services.service import ResumeService

logger = get_logger(__name__)


class CompatibilityService:
    """Orchestrates job compatibility analysis for candidates."""

    def __init__(
        self,
        resume_service: Optional[ResumeService] = None,
        engine: Optional[CompatibilityEngine] = None,
    ) -> None:
        self.resume_service = resume_service or ResumeService()
        self.engine = engine or CompatibilityEngine()

    async def analyze_compatibility(
        self, resume: ResumeIntelligenceReport, job: JobIntelligenceReport
    ) -> CompatibilityReport:
        """Directly compare a resume intelligence report against a job intelligence report.

        Args:
            resume: ResumeIntelligenceReport.
            job: JobIntelligenceReport.

        Returns:
            CompatibilityReport.
        """
        start_time = time.perf_counter()
        logger.info("Starting direct compatibility analysis")
        try:
            report = self.engine.analyze(resume, job)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "Direct compatibility analysis completed successfully",
                duration_ms=duration_ms,
            )
            return report
        except Exception as e:
            logger.error("Direct compatibility analysis failed", error=str(e))
            raise

    async def analyze_compatibility_by_job_id(
        self, resume_pdf_path: str, job_id: str, db: AsyncSession
    ) -> CompatibilityReport:
        """Analyze compatibility by parsing a resume PDF and loading a job description from database by ID.

        Args:
            resume_pdf_path: Local path to the candidate's resume PDF.
            job_id: The UUID of the job description in the database.
            db: AsyncSession database session.

        Returns:
            CompatibilityReport.
        """
        start_time = time.perf_counter()
        logger.info("Starting compatibility analysis by Job ID", job_id=job_id)
        try:
            # 1. Parse resume
            resume_report = await self.resume_service.analyze_resume(resume_pdf_path)

            # 2. Load Job Intelligence Report from DB using latest ProcessingRun pipeline state
            try:
                job_uuid = uuid.UUID(job_id)
            except ValueError as e:
                raise ValueError(f"Invalid job_id UUID format: {job_id}") from e

            stmt = (
                select(ProcessingRun)
                .where(ProcessingRun.job_id == job_uuid)
                .order_by(ProcessingRun.started_at.desc())
                .limit(1)
            )
            result = await db.execute(stmt)
            run_record = result.scalars().first()

            if not run_record or not run_record.pipeline_state:
                raise FileNotFoundError(
                    f"No processed pipeline state found for job_id: {job_id}"
                )

            job_report = ResponseBuilder.build_report(run_record.pipeline_state)

            # 3. Match
            report = self.engine.analyze(resume_report, job_report)

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "Compatibility analysis by Job ID completed successfully",
                job_id=job_id,
                duration_ms=duration_ms,
            )
            return report
        except Exception as e:
            logger.error(
                "Compatibility analysis by Job ID failed", job_id=job_id, error=str(e)
            )
            raise

    async def analyze_compatibility_by_job_url(
        self, resume_pdf_path: str, job_url: str, db: AsyncSession
    ) -> CompatibilityReport:
        """Analyze compatibility by parsing a resume PDF and scraping/parsing a Job URL.

        Args:
            resume_pdf_path: Local path to the candidate's resume PDF.
            job_url: The URL of the job description.
            db: AsyncSession database session.

        Returns:
            CompatibilityReport.
        """
        start_time = time.perf_counter()
        logger.info("Starting compatibility analysis by Job URL", url=job_url)
        try:
            # 1. Analyze resume
            resume_report = await self.resume_service.analyze_resume(resume_pdf_path)

            # 2. Fetch and analyze job URL via E2E JD Pipeline
            pipeline_service = PipelineService(db)
            final_state = await pipeline_service.run_pipeline(url=job_url)

            if final_state.get("errors") and not final_state.get("raw_document"):
                raise RuntimeError(
                    f"Job description parsing failed: {', '.join(final_state['errors'])}"
                )

            job_report = ResponseBuilder.build_report(final_state)

            # 3. Calculate compatibility
            report = self.engine.analyze(resume_report, job_report)

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "Compatibility analysis by Job URL completed successfully",
                url=job_url,
                duration_ms=duration_ms,
            )
            return report
        except Exception as e:
            logger.error(
                "Compatibility analysis by Job URL failed", url=job_url, error=str(e)
            )
            raise

    async def analyze_compatibility_by_job_pdf(
        self, resume_pdf_path: str, job_pdf_path: str, db: AsyncSession
    ) -> CompatibilityReport:
        """Analyze compatibility by comparing an uploaded resume PDF against an uploaded/local job PDF.

        Args:
            resume_pdf_path: Local path to the candidate's resume PDF.
            job_pdf_path: Local path to the job description PDF.
            db: AsyncSession database session.

        Returns:
            CompatibilityReport.
        """
        start_time = time.perf_counter()
        logger.info("Starting compatibility analysis by Job PDF", job_pdf=job_pdf_path)
        try:
            # 1. Analyze resume
            resume_report = await self.resume_service.analyze_resume(resume_pdf_path)

            # 2. Analyze Job PDF via E2E JD Pipeline
            pipeline_service = PipelineService(db)
            final_state = await pipeline_service.run_pipeline(pdf_path=job_pdf_path)

            if final_state.get("errors") and not final_state.get("raw_document"):
                raise RuntimeError(
                    f"Job description parsing failed: {', '.join(final_state['errors'])}"
                )

            job_report = ResponseBuilder.build_report(final_state)

            # 3. Calculate compatibility
            report = self.engine.analyze(resume_report, job_report)

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "Compatibility analysis by Job PDF completed successfully",
                job_pdf=job_pdf_path,
                duration_ms=duration_ms,
            )
            return report
        except Exception as e:
            logger.error(
                "Compatibility analysis by Job PDF failed",
                job_pdf=job_pdf_path,
                error=str(e),
            )
            raise
