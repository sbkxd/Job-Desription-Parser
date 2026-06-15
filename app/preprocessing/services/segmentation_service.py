"""Segmentation service — orchestrates the job description preprocessing pipeline."""

import time
from datetime import datetime

from app.logging.logger import get_logger
from app.preprocessing.classifiers.boilerplate_detector import BoilerplateDetector
from app.preprocessing.classifiers.section_classifier import SectionClassifier
from app.preprocessing.cleaners.text_cleaner import TextCleaner
from app.preprocessing.noise.services.noise_filter import NoiseFilterService
from app.preprocessing.noise.validators.section_purifier import SectionPurifier
from app.preprocessing.schemas.schemas import (
    RawDocument,
    Section,
    SegmentationResult,
    SegmentedDocument,
)
from app.preprocessing.segmenters.section_segmenter import SectionSegmenter

logger = get_logger(__name__)


class SegmentationService:
    """Orchestrates cleaning, boilerplate removal, noise filtering, and section classification."""

    def __init__(self) -> None:
        self.cleaner = TextCleaner()
        self.boilerplate_detector = BoilerplateDetector()
        self.segmenter = SectionSegmenter()
        self.classifier = SectionClassifier()
        self.noise_filter = NoiseFilterService()
        self.section_purifier = SectionPurifier()

    def segment(self, raw_document: RawDocument) -> SegmentationResult:
        """Run the full JD segmentation pipeline on a raw document.

        Args:
            raw_document: The input RawDocument structure.

        Returns:
            SegmentationResult containing the SegmentedDocument on success,
            or the error details on failure.
        """
        start_time = time.perf_counter()
        raw_text = getattr(raw_document, "raw_text", None) or ""
        logger.info(
            "Starting job description segmentation pipeline",
            source_type=getattr(raw_document, "source_type", None),
            source_url=getattr(raw_document, "source_url", None),
            raw_text_len=len(raw_text),
        )

        try:
            if (
                not getattr(raw_document, "raw_text", None)
                or not raw_document.raw_text.strip()
            ):
                raise ValueError("raw_text must not be empty")

            # 1. Clean the raw text
            cleaned_text = self.cleaner.clean(raw_document.raw_text)

            # 2. Split into lines
            lines = [ln.strip() for ln in cleaned_text.split("\n")]

            # 3. Run Noise Filtering Layer (Milestone 4)
            filtered_lines, noise_metrics = self.noise_filter.filter_noise(
                lines, source_type=getattr(raw_document, "source_type", None)
            )

            # 4. Detect boilerplate
            clean_lines, boilerplate_blocks = self.boilerplate_detector.detect(
                filtered_lines
            )

            # 5. Segment into raw sections
            raw_sections = self.segmenter.segment(clean_lines)

            # 6. Classify each section
            sections: list[Section] = []
            for raw_sec in raw_sections:
                final_type, confidence = self.classifier.classify(
                    heading=raw_sec.heading,
                    lines=raw_sec.lines,
                    detected_type=raw_sec.detected_type,
                    heading_confidence=raw_sec.confidence,
                )
                sections.append(
                    Section(
                        section_type=final_type,
                        heading=raw_sec.heading,
                        lines=raw_sec.lines,
                        confidence=confidence,
                    )
                )

            # 7. Run Section Purification and Quality Scoring (Milestone 5 & 7)
            purified_sections, quality_scores = self.section_purifier.purify_sections(
                sections
            )

            # Construct the final segmented document
            segmented_doc = SegmentedDocument(
                sections=purified_sections,
                boilerplate_removed=boilerplate_blocks,
                segmented_at=datetime.utcnow(),
                source_type=raw_document.source_type,
                source_url=raw_document.source_url,
                metadata={
                    "cleaned_lines_count": len(clean_lines),
                    "boilerplate_blocks_count": len(boilerplate_blocks),
                    "raw_sections_count": len(raw_sections),
                    "noise_removed_lines": noise_metrics.get("removed_lines", 0),
                    "noise_metrics": noise_metrics,
                    "section_quality_scores": quality_scores,
                },
            )

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "Job description segmentation pipeline completed successfully",
                duration_ms=round(duration_ms, 2),
                sections_count=len(sections),
            )

            return SegmentationResult(
                success=True,
                document=segmented_doc,
                duration_ms=round(duration_ms, 2),
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.exception(
                "Job description segmentation pipeline failed",
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
            return SegmentationResult(
                success=False,
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
