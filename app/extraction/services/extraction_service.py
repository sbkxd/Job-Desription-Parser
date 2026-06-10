"""Extraction orchestrator service."""

import time

from app.extraction.experience.experience_extractor import ExperienceExtractor
from app.extraction.requirements.requirement_classifier import RequirementClassifier
from app.extraction.schemas.schemas import ExtractionResult
from app.extraction.seniority.seniority_extractor import SeniorityExtractor
from app.extraction.skills.skills_extractor import SkillsExtractor
from app.logging.logger import get_logger

logger = get_logger(__name__)


class ExtractionService:
    """Orchestrates the information extraction pipeline from segmented job description data."""

    def __init__(self) -> None:
        self.skills_extractor = SkillsExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.seniority_extractor = SeniorityExtractor()
        self.requirement_classifier = RequirementClassifier()

    def extract(self, segmented_document: dict[str, list[str]]) -> ExtractionResult:
        """Run the full information extraction pipeline.

        Args:
            segmented_document: Dictionary holding keys matching SectionType enum
                                (responsibilities, requirements, nice_to_have, about_company, benefits, other)
                                and their text line lists.

        Returns:
            ExtractionResult.
        """
        start_time = time.perf_counter()
        logger.info("Starting information extraction pipeline")

        try:
            # 1. Skill Extraction
            skills = self.skills_extractor.extract(segmented_document)

            # 2. Experience Extraction
            experience = self.experience_extractor.extract(segmented_document)

            # 3. Seniority Extraction
            seniority = self.seniority_extractor.extract(
                segmented_document, experience=experience
            )

            # 4. Requirement Classification
            req_classifications = self.requirement_classifier.classify(
                segmented_document
            )

            # 5. Validation and cleaning of outputs
            if experience.min_years is not None and experience.max_years is not None:
                if experience.min_years > experience.max_years:
                    # Correct invalid ranges where min > max
                    experience.min_years, experience.max_years = (
                        experience.max_years,
                        experience.min_years,
                    )

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "Information extraction pipeline completed successfully",
                duration_ms=round(duration_ms, 2),
                skills_count=len(skills),
                requirements_classified=len(req_classifications),
            )

            return ExtractionResult(
                success=True,
                skills=skills,
                experience=experience,
                seniority=seniority,
                requirements_classification=req_classifications,
                duration_ms=round(duration_ms, 2),
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.exception(
                "Information extraction pipeline failed",
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
            return ExtractionResult(
                success=False,
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
