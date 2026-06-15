"""Noise Filter Service sanitizing raw lines and platform-specific board artifacts."""

from typing import Dict, List, Tuple

from app.preprocessing.noise.rules import (
    AtsArtifactRule,
    ContactInfoRule,
    JobBoardRule,
    LegalRule,
    LinkedInArtifactRule,
    MetadataRule,
    NavigationRule,
)


class NoiseFilterService:
    """Orchestrates line-level filtering and platform-specific cleanup."""

    def __init__(self) -> None:
        self.contact_rule = ContactInfoRule()
        self.ats_rule = AtsArtifactRule()
        self.linkedin_rule = LinkedInArtifactRule()
        self.job_board_rule = JobBoardRule()
        self.metadata_rule = MetadataRule()
        self.legal_rule = LegalRule()
        self.navigation_rule = NavigationRule()

    def _is_platform_noise(
        self, line_clean: str, source_lower: str, metrics: Dict[str, int]
    ) -> bool:
        """Check if the line is platform-specific noise and update metrics."""
        if (
            source_lower == "linkedin"
            and self.linkedin_rule.evaluate(line_clean)["is_noise"]
        ):
            metrics["linkedin_artifacts"] += 1
            return True

        if (
            source_lower == "naukri"
            and self.job_board_rule.evaluate(line_clean)["is_noise"]
        ):
            metrics["job_board_artifacts"] += 1
            return True

        if source_lower == "foundit" and any(
            x in line_clean.lower()
            for x in ["all rights reserved", "terms of use", "privacy statement"]
        ):
            metrics["job_board_artifacts"] += 1
            return True

        if (
            source_lower == "greenhouse"
            and self.navigation_rule.evaluate(line_clean)["is_noise"]
        ):
            metrics["navigation_text"] += 1
            return True

        if source_lower == "lever" and any(
            x in line_clean.lower() for x in ["similar jobs", "people also viewed"]
        ):
            metrics["linkedin_artifacts"] += 1
            return True

        if (
            source_lower == "workable"
            and self.ats_rule.evaluate(line_clean)["is_noise"]
        ):
            metrics["ats_artifacts"] += 1
            return True

        return False

    def _is_general_noise(self, line_clean: str, metrics: Dict[str, int]) -> bool:
        """Check if the line matches any general noise rules and update metrics."""
        if self.contact_rule.evaluate(line_clean)["is_noise"]:
            metrics["contact_info"] += 1
            return True

        if self.ats_rule.evaluate(line_clean)["is_noise"]:
            metrics["ats_artifacts"] += 1
            return True

        if self.metadata_rule.evaluate(line_clean)["is_noise"]:
            metrics["employment_metadata"] += 1
            return True

        if self.legal_rule.evaluate(line_clean)["is_noise"]:
            metrics["company_legal_text"] += 1
            return True

        if self.navigation_rule.evaluate(line_clean)["is_noise"]:
            metrics["navigation_text"] += 1
            return True

        return False

    def filter_noise(
        self, lines: List[str], source_type: str | None = None
    ) -> Tuple[List[str], Dict[str, int]]:
        """Remove noise, metadata blocks, and platform-specific artifacts from raw lines.

        Args:
            lines: The list of raw text lines.
            source_type: The source platform of the job description.

        Returns:
            A tuple of (purified_lines, metrics_dict).
        """
        purified_lines: List[str] = []
        metrics: Dict[str, int] = {
            "contact_info": 0,
            "ats_artifacts": 0,
            "linkedin_artifacts": 0,
            "job_board_artifacts": 0,
            "employment_metadata": 0,
            "company_legal_text": 0,
            "navigation_text": 0,
            "removed_lines": 0,
        }

        source_lower = (source_type or "").lower()

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            if self._is_platform_noise(line_clean, source_lower, metrics):
                metrics["removed_lines"] += 1
                continue

            if self._is_general_noise(line_clean, metrics):
                metrics["removed_lines"] += 1
                continue

            # If it passes all filters, it is valid content
            purified_lines.append(line)

        return purified_lines, metrics
