"""Requirement classification engine."""

import re

from app.extraction.schemas.schemas import RequirementClassification

# Keywords indicating required status
_REQUIRED_KEYWORDS = [
    r"\bmust\b",
    r"\brequired\b",
    r"\bessential\b",
    r"\bmandatory\b",
    r"\bexpect(ed)?\b",
    r"\bneed(s|ed)?\b",
    r"\bhave\s+to\b",
    r"\bshould\b",
    r"\bqualification(s)?\b",
    r"\bdegree\b",
]

# Keywords indicating preferred status
_PREFERRED_KEYWORDS = [
    r"\bprefer(red)?\b",
    r"\bplus\b",
    r"\bbonus\b",
    r"\badvantage\b",
    r"\bdesir(able|ed)?\b",
    r"\bhighly\s+regarded\b",
    r"\bideally?\b",
    r"\bstrong\s+plus\b",
]

# Keywords indicating optional status
_OPTIONAL_KEYWORDS = [
    r"\bnice\s+to\s+have(s)?\b",
    r"\boptional\b",
    r"\bgood\s+to\s+have\b",
    r"\bhelpful\b",
    r"\bbeneficial\b",
]

# Compile patterns
_RE_REQUIRED = re.compile("|".join(_REQUIRED_KEYWORDS), re.IGNORECASE)
_RE_PREFERRED = re.compile("|".join(_PREFERRED_KEYWORDS), re.IGNORECASE)
_RE_OPTIONAL = re.compile("|".join(_OPTIONAL_KEYWORDS), re.IGNORECASE)


class RequirementClassifier:
    """Classifies job requirements into Required, Preferred, or Optional categories."""

    def classify_line(
        self, line: str, default_classification: str = "Required"
    ) -> RequirementClassification:
        """Classify a single requirement line using deterministic keyword patterns.

        Args:
            line: The text line of the requirement.
            default_classification: Default classification to use if no keyword triggers.

        Returns:
            RequirementClassification object.
        """
        stripped = line.strip()
        if not stripped:
            return RequirementClassification(
                text="", classification="Required", confidence=0.0
            )

        # 1. Match Optional (often overlaps, so check first/explicitly)
        if _RE_OPTIONAL.search(stripped):
            return RequirementClassification(
                text=stripped,
                classification="Optional",
                confidence=0.95,
            )

        # 2. Match Preferred
        if _RE_PREFERRED.search(stripped):
            return RequirementClassification(
                text=stripped,
                classification="Preferred",
                confidence=0.95,
            )

        # 3. Match Required
        if _RE_REQUIRED.search(stripped):
            return RequirementClassification(
                text=stripped,
                classification="Required",
                confidence=0.95,
            )

        # 4. Fallback to default classification
        return RequirementClassification(
            text=stripped,
            classification=default_classification,
            confidence=0.7,
        )

    def classify(
        self, sections: dict[str, list[str]]
    ) -> list[RequirementClassification]:
        """Classify all requirement lines from the requirements and nice_to_have sections."""
        results: list[RequirementClassification] = []

        # Process 'requirements' section with 'Required' default
        for line in sections.get("requirements", []):
            if line.strip():
                results.append(
                    self.classify_line(line, default_classification="Required")
                )

        # Process 'nice_to_have' section with 'Optional' default
        for line in sections.get("nice_to_have", []):
            if line.strip():
                results.append(
                    self.classify_line(line, default_classification="Optional")
                )

        return results
