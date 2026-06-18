"""Service layer coordinating Mistral Resume Recommendations and Optimization."""

import time
from typing import Optional

from app.compatibility.services.service import CompatibilityService
from app.logging.logger import get_logger
from app.orchestration.mistral.mistral_client import MistralClient
from app.presentation.schemas.job_intelligence import JobIntelligenceReport
from app.recommendations.prompts.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.recommendations.schemas.schemas import (
    MistralRecommendationsResponse,
    ResumeOptimizationReport,
)
from app.resume.schemas.schemas import ResumeIntelligenceReport

logger = get_logger(__name__)


class RecommendationService:
    """Orchestrates the Mistral-based resume optimization suggestions."""

    def __init__(
        self,
        mistral_client: Optional[MistralClient] = None,
        compatibility_service: Optional[CompatibilityService] = None,
    ) -> None:
        self.mistral_client = mistral_client or MistralClient()
        self.compatibility_service = compatibility_service or CompatibilityService()

    async def generate_recommendations(
        self, resume: ResumeIntelligenceReport, job: JobIntelligenceReport
    ) -> ResumeOptimizationReport:
        """Analyze compatibility and call Mistral to generate resume optimization recommendations.

        Args:
            resume: The candidate's pre-parsed resume intelligence.
            job: The job description intelligence.

        Returns:
            The combined ResumeOptimizationReport.
        """
        start_time = time.perf_counter()
        logger.info("Starting resume optimization recommendations generation")

        try:
            # 1. Run compatibility engine to get scores, gaps, and strengths
            compat_report = await self.compatibility_service.analyze_compatibility(
                resume, job
            )

            # 2. Structure input reports as JSON strings for LLM prompt
            resume_json = resume.model_dump_json(indent=2)
            job_json = job.model_dump_json(indent=2)
            compatibility_json = compat_report.model_dump_json(indent=2)

            user_prompt = USER_PROMPT_TEMPLATE.format(
                resume_json=resume_json,
                job_json=job_json,
                compatibility_json=compatibility_json,
            )

            # 3. Request structured recommendations from Mistral
            logger.info("Invoking Mistral for structured recommendations")
            mistral_resp = await self.mistral_client.generate_structured(
                prompt=user_prompt,
                schema=MistralRecommendationsResponse,
                system_prompt=SYSTEM_PROMPT,
                prompt_version="resume_optimization_v1",
            )

            # 4. Compile the final unified report
            report = ResumeOptimizationReport(
                compatibility_score=compat_report.compatibility_score,
                matched_skills=compat_report.skill_match.matched,
                missing_skills=compat_report.skill_match.missing,
                critical_gaps=compat_report.gap_analysis.critical_gaps,
                strengths=compat_report.strength_analysis.strong_matches,
                resume_improvements=mistral_resp.resume_improvements,
                ats_recommendations=mistral_resp.ats_recommendations,
                application_readiness_score=mistral_resp.application_readiness_score,
                application_readiness_recommendation=mistral_resp.application_readiness_recommendation,
                tailored_summary=mistral_resp.tailored_summary,
            )

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "Successfully generated resume optimization report",
                duration_ms=duration_ms,
                compatibility_score=report.compatibility_score,
                readiness_score=report.application_readiness_score,
            )
            return report

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                "Resume optimization recommendations generation failed",
                duration_ms=duration_ms,
                error=str(e),
            )
            raise
