"""Resume analysis service coordinating parsing, extraction, and normalization."""

import time
from typing import Optional

from app.logging.logger import get_logger
from app.normalization.services.normalization_service import SkillNormalizationService
from app.resume.extraction.extractor import ResumeExtractor
from app.resume.ingestion.parser import ResumeParser
from app.resume.schemas.schemas import ResumeIntelligenceReport, ResumeSkill

logger = get_logger(__name__)


class ResumeService:
    """Orchestrates the resume analysis pipeline."""

    def __init__(
        self,
        parser: Optional[ResumeParser] = None,
        extractor: Optional[ResumeExtractor] = None,
        normalizer: Optional[SkillNormalizationService] = None,
    ) -> None:
        self.parser = parser or ResumeParser()
        self.extractor = extractor or ResumeExtractor()
        self.normalizer = normalizer or SkillNormalizationService()

    async def analyze_resume(self, pdf_path: str) -> ResumeIntelligenceReport:
        """Parse, extract, and normalize resume from a local PDF path.

        Args:
            pdf_path: Local filesystem path to the resume PDF.

        Returns:
            The complete ResumeIntelligenceReport.
        """
        start_time = time.perf_counter()
        logger.info("Starting resume analysis service", pdf_path=pdf_path)

        try:
            # 1. Ingestion: PDF parsing
            raw_text = self.parser.parse(pdf_path)
            if not raw_text.strip():
                raise ValueError("Extracted text from resume PDF is empty.")

            # 2. Extraction: LLM-based structured extraction
            report = await self.extractor.extract(raw_text)

            # 3. Normalization: Normalize raw skills using the existing normalization framework
            if report.skills:
                raw_skill_names = [s.raw_skill for s in report.skills if s.raw_skill]

                if raw_skill_names:
                    norm_result = self.normalizer.normalize(raw_skill_names)

                    # Map normalization results back to ResumeSkill schemas
                    normalized_skills = []
                    for ns in norm_result.normalized_skills:
                        normalized_skills.append(
                            ResumeSkill(
                                raw_skill=ns.raw_skill,
                                normalized_skill=ns.normalized_skill,
                                confidence=ns.confidence,
                                esco_id=ns.esco_id,
                            )
                        )
                    report.skills = normalized_skills

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "Resume analysis service completed successfully",
                pdf_path=pdf_path,
                duration_ms=duration_ms,
                skills_count=len(report.skills),
            )
            return report

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                "Resume analysis service failed",
                pdf_path=pdf_path,
                duration_ms=duration_ms,
                error=str(e),
            )
            raise
