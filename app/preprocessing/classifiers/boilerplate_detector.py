"""Boilerplate detection — identifies and quarantines non-JD content.

Detects and removes equal opportunity statements, legal disclaimers,
recruitment marketing copy, privacy notices, and application instructions.

Removed content is never permanently discarded — it is returned as a
list of BoilerplateBlock objects for audit/debugging.
"""

import re
from dataclasses import dataclass, field

from app.preprocessing.schemas.schemas import BoilerplateBlock, BoilerplateCategory

# ---------------------------------------------------------------------------
# Pattern definitions per category
# ---------------------------------------------------------------------------
# Each entry is (compiled regex pattern, BoilerplateCategory)
# Patterns are matched against lowercased line text.
# ---------------------------------------------------------------------------

_EEO_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"equal opportunity employer", re.I),
    re.compile(r"equal employment opportunity", re.I),
    re.compile(r"eeo employer", re.I),
    re.compile(r"without regard to race", re.I),
    re.compile(r"without regard to age", re.I),
    re.compile(r"regardless of race", re.I),
    re.compile(r"regardless of gender", re.I),
    re.compile(r"affirmative action", re.I),
    re.compile(r"diversity.{0,30}inclusion", re.I),
    re.compile(r"we do not discriminate", re.I),
    re.compile(r"protected veteran", re.I),
    re.compile(r"individuals with disabilities", re.I),
    re.compile(r"all qualified applicants", re.I),
]

_LEGAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"all rights reserved", re.I),
    re.compile(r"terms and conditions", re.I),
    re.compile(r"subject to background check", re.I),
    re.compile(r"background verification", re.I),
    re.compile(r"at.will employment", re.I),
    re.compile(r"employment is contingent", re.I),
    re.compile(r"this job description is not exhaustive", re.I),
    re.compile(r"management reserves the right", re.I),
    re.compile(r"duties may change", re.I),
    re.compile(r"may be modified at any time", re.I),
]

_PRIVACY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"privacy policy", re.I),
    re.compile(r"data protection", re.I),
    re.compile(r"gdpr", re.I),
    re.compile(r"personal data", re.I),
    re.compile(r"information collected", re.I),
    re.compile(r"candidate data", re.I),
    re.compile(r"your data will be", re.I),
]

_APPLICATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"how to apply", re.I),
    re.compile(r"to apply.{0,30}click", re.I),
    re.compile(r"apply (now|today|online)", re.I),
    re.compile(r"submit your (resume|cv|application)", re.I),
    re.compile(r"send your (resume|cv) to", re.I),
    re.compile(r"email your (resume|cv)", re.I),
    re.compile(r"applications? (will be|are being|are)", re.I),
    re.compile(r"only shortlisted candidates", re.I),
    re.compile(r"shortlisted candidates will", re.I),
    re.compile(r"only selected candidates", re.I),
    re.compile(r"no phone calls please", re.I),
    re.compile(r"please do not call", re.I),
    re.compile(r"we regret (that )?only", re.I),
    re.compile(r"deadline for applications", re.I),
    re.compile(r"closing date", re.I),
]

_RECRUITMENT_MARKETING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"we are an innovative", re.I),
    re.compile(r"fast.growing (startup|company|team)", re.I),
    re.compile(r"join our (amazing|awesome|dynamic|talented|passionate) team", re.I),
    re.compile(r"world.class (team|company|organization)", re.I),
    re.compile(r"award.winning (company|team|organization)", re.I),
    re.compile(r"disrupt(?:ing|ive).{0,40}industry", re.I),
    re.compile(r"rockstar developer", re.I),
    re.compile(r"10x engineer", re.I),
    re.compile(r"ninja developer", re.I),
]

_GENERIC_POLICY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"note:.{0,80}salary", re.I),
    re.compile(r"compensation will be commensurate", re.I),
    re.compile(r"we are unable to (offer|provide) (visa|sponsorship)", re.I),
    re.compile(r"visa sponsorship (is not|not) available", re.I),
    re.compile(r"must be (authorized|eligible) to work", re.I),
    re.compile(r"must have (a )?valid work (authorization|permit)", re.I),
    re.compile(r"work authorization required", re.I),
]

_ALL_PATTERNS: list[tuple[list[re.Pattern[str]], BoilerplateCategory]] = [
    (_EEO_PATTERNS, BoilerplateCategory.EQUAL_OPPORTUNITY),
    (_LEGAL_PATTERNS, BoilerplateCategory.LEGAL_DISCLAIMER),
    (_PRIVACY_PATTERNS, BoilerplateCategory.PRIVACY_STATEMENT),
    (_APPLICATION_PATTERNS, BoilerplateCategory.APPLICATION_INSTRUCTIONS),
    (_RECRUITMENT_MARKETING_PATTERNS, BoilerplateCategory.RECRUITMENT_MARKETING),
    (_GENERIC_POLICY_PATTERNS, BoilerplateCategory.GENERIC_POLICY),
]

# Minimum length for a line to be a boilerplate candidate (short lines
# like "Note:" alone should not trigger detection).
_MIN_BOILERPLATE_LINE_LENGTH = 20


@dataclass
class _PendingBlock:
    """Accumulates consecutive boilerplate lines before committing."""

    category: BoilerplateCategory
    lines: list[str] = field(default_factory=list)
    start_idx: int = 0


class BoilerplateDetector:
    """Rule-based boilerplate content detector.

    Scans a list of text lines and separates job-description content
    from boilerplate. Removed content is preserved in BoilerplateBlock
    objects.

    Usage::

        detector = BoilerplateDetector()
        clean_lines, removed = detector.detect(lines)
    """

    def detect(self, lines: list[str]) -> tuple[list[str], list[BoilerplateBlock]]:
        """Separate JD content lines from boilerplate.

        Args:
            lines: Input lines from the cleaned/normalized text.

        Returns:
            (clean_lines, removed_blocks) where:
                - clean_lines: lines that are not boilerplate
                - removed_blocks: BoilerplateBlock list (never empty if
                  boilerplate was detected)
        """
        clean_lines: list[str] = []
        removed_blocks: list[BoilerplateBlock] = []
        pending: _PendingBlock | None = None

        for idx, line in enumerate(lines):
            category = self._classify_line(line)

            if category is not None:
                # Start or extend a boilerplate block
                if pending is None or pending.category != category:
                    if pending is not None:
                        removed_blocks.append(
                            BoilerplateBlock(
                                category=pending.category,
                                lines=pending.lines,
                                start_line_idx=pending.start_idx,
                            )
                        )
                    pending = _PendingBlock(
                        category=category, lines=[line], start_idx=idx
                    )
                else:
                    pending.lines.append(line)
            else:
                # Flush any open boilerplate block
                if pending is not None:
                    removed_blocks.append(
                        BoilerplateBlock(
                            category=pending.category,
                            lines=pending.lines,
                            start_line_idx=pending.start_idx,
                        )
                    )
                    pending = None
                clean_lines.append(line)

        # Flush trailing boilerplate block
        if pending is not None:
            removed_blocks.append(
                BoilerplateBlock(
                    category=pending.category,
                    lines=pending.lines,
                    start_line_idx=pending.start_idx,
                )
            )

        return clean_lines, removed_blocks

    @staticmethod
    def _classify_line(line: str) -> BoilerplateCategory | None:
        """Return the boilerplate category for a line, or None if clean."""
        stripped = line.strip()
        if len(stripped) < _MIN_BOILERPLATE_LINE_LENGTH:
            return None

        for patterns, category in _ALL_PATTERNS:
            for pattern in patterns:
                if pattern.search(stripped):
                    return category
        return None
