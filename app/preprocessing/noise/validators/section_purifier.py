"""Section Purifier validating and cleaning segmented sections post-segmentation."""

from typing import Dict, List, Tuple

from app.preprocessing.noise.classifiers.content_classifier import ContentTypeClassifier
from app.preprocessing.schemas.schemas import Section


class SectionPurifier:
    """Validates individual sections, purges invalid lines, and calculates quality metrics."""

    def __init__(self) -> None:
        self.classifier = ContentTypeClassifier()

    def _is_allowed_line(self, sec_type: str, line_type: str) -> bool:
        """Check if a line content type is allowed in the given section type."""
        if sec_type == "responsibilities":
            # Reject: NOISE, CONTACT_INFO, METADATA
            return line_type not in ["NOISE", "CONTACT_INFO", "METADATA"]

        if sec_type in ("requirements", "nice_to_have"):
            # Reject: NOISE, CONTACT_INFO, METADATA, BENEFIT, COMPANY_INFO
            return line_type not in [
                "NOISE",
                "CONTACT_INFO",
                "METADATA",
                "BENEFIT",
                "COMPANY_INFO",
            ]

        if sec_type == "benefits":
            # Reject: NOISE, CONTACT_INFO, METADATA, COMPANY_INFO
            return line_type not in [
                "NOISE",
                "CONTACT_INFO",
                "METADATA",
                "COMPANY_INFO",
            ]

        # Default fallback for other sections
        return line_type != "NOISE"

    def purify_sections(
        self, sections: List[Section]
    ) -> Tuple[List[Section], Dict[str, Dict[str, float]]]:
        """Purge non-compliant lines from sections and calculate quality metrics.

        Args:
            sections: The list of raw classified Sections.

        Returns:
            A tuple of (purified_sections, quality_scores_dict).
        """
        purified_sections: List[Section] = []
        quality_scores: Dict[str, Dict[str, float]] = {}

        for sec in sections:
            sec_type = sec.section_type.lower()
            original_line_count = len(sec.lines)
            if original_line_count == 0:
                quality_scores[sec_type] = {"quality": 1.0}
                purified_sections.append(sec)
                continue

            purified_lines: List[str] = []

            for line in sec.lines:
                line_clean = line.strip()
                if not line_clean:
                    continue

                # Classify the line content type
                line_type = self.classifier.classify_line(line_clean)

                if self._is_allowed_line(sec_type, line_type):
                    purified_lines.append(line)

            # Calculate quality score
            purified_line_count = len(purified_lines)
            quality_score = (
                purified_line_count / original_line_count
                if original_line_count > 0
                else 1.0
            )

            quality_scores[sec_type] = {"quality": round(quality_score, 2)}

            # Only append section if it has remaining lines, otherwise it is fully noise
            if purified_line_count > 0:
                purified_sections.append(
                    Section(
                        section_type=sec.section_type,
                        heading=sec.heading,
                        lines=purified_lines,
                        confidence=sec.confidence,
                    )
                )

        return purified_sections, quality_scores
