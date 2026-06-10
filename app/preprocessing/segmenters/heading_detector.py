"""Heading detection engine — identifies section boundary lines.

Uses a multi-strategy approach:
1. Exact alias table lookup (highest confidence)
2. RapidFuzz fuzzy match against known headings (configurable threshold)
3. Structural heuristics (short line, ends with colon, all-caps, title-case)
"""

import re

from rapidfuzz import fuzz

from app.preprocessing.normalizers.heading_normalizer import HeadingNormalizer
from app.preprocessing.schemas.schemas import SectionType

# ---------------------------------------------------------------------------
# Compiled heuristic patterns
# ---------------------------------------------------------------------------

_RE_TRAILING_COLON = re.compile(r":\s*$")
_RE_ALL_CAPS = re.compile(r"^[A-Z][A-Z\s/&',\-]{3,60}$")
_RE_TITLE_CASE_ISOLATED = re.compile(
    r"^(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[A-Z]{2,}(?:\s+[A-Z]{2,})*)$"
)

# Maximum word count for a line to be a heading candidate
_MAX_HEADING_WORDS = 10
# Minimum character length for heuristic heading detection
_MIN_HEADING_CHARS = 3
# Fuzzy match threshold (0–100)
_FUZZY_THRESHOLD = 82

# Pre-compute all canonical heading keys for fuzzy matching
_normalizer = HeadingNormalizer()
_CANONICAL_KEYS: list[str] = list(_normalizer.alias_table.keys())


class HeadingDetector:
    """Multi-strategy heading detector for job description text.

    Strategies (in priority order):
    1. Exact alias lookup → confident SectionType
    2. RapidFuzz partial match → probable SectionType with lower confidence
    3. Structural heuristics → ``is_heading=True`` with no type resolved

    Usage::

        detector = HeadingDetector()
        if detector.is_heading(line):
            section_type = detector.classify_heading(line)
    """

    def __init__(self, fuzzy_threshold: int = _FUZZY_THRESHOLD) -> None:
        self._normalizer = HeadingNormalizer()
        self.fuzzy_threshold = fuzzy_threshold

    def is_heading(self, line: str) -> bool:
        """Return True if the line is likely a section heading.

        Checks alias table first, then fuzzy match, then structural
        heuristics.  Returns False for empty lines and lines with too
        many words.
        """
        stripped = line.strip()
        if not stripped or len(stripped) < _MIN_HEADING_CHARS:
            return False

        word_count = len(stripped.split())
        if word_count > _MAX_HEADING_WORDS:
            return False

        # Strategy 1: exact alias match
        if self._normalizer.resolve(stripped) is not None:
            return True

        # Strategy 2: fuzzy match
        if self._fuzzy_match(stripped) is not None:
            return True

        # Strategy 3: structural heuristics
        return self._structural_heuristic(stripped)

    def classify_heading(self, line: str) -> tuple[SectionType | None, float]:
        """Return (SectionType, confidence) for a heading line.

        Confidence scale:
        - 1.0  : exact alias match
        - 0.85–0.99 : fuzzy match above threshold
        - 0.5  : structural heuristic only (type unknown → OTHER)
        - None : not a heading
        """
        stripped = line.strip()
        if not stripped:
            return None, 0.0

        # Strategy 1: exact alias
        section_type = self._normalizer.resolve(stripped)
        if section_type is not None:
            return section_type, 1.0

        # Strategy 2: fuzzy match
        fuzzy_result = self._fuzzy_match(stripped)
        if fuzzy_result is not None:
            matched_key, score = fuzzy_result
            section_type = _normalizer.alias_table[matched_key]
            confidence = round(score / 100.0, 2)
            return section_type, confidence

        # Strategy 3: heuristic — type unknown
        if self._structural_heuristic(stripped):
            return None, 0.5

        return None, 0.0

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fuzzy_match(self, line: str) -> tuple[str, float] | None:
        """Find the best fuzzy match in the alias table.

        Returns (matched_key, score) if above threshold, else None.
        """
        key = self._normalizer.normalize_key(line)
        if not key:
            return None

        best_score = 0.0
        best_key = ""
        for canonical in _CANONICAL_KEYS:
            score = float(fuzz.token_sort_ratio(key, canonical))
            if score > best_score:
                best_score = score
                best_key = canonical

        if best_score >= self.fuzzy_threshold:
            return best_key, best_score
        return None

    @staticmethod
    def _structural_heuristic(line: str) -> bool:
        """Apply structural rules to detect unlisted headings.

        Positive signals:
        - Line ends with ':'
        - Line is all-caps (3–60 chars)
        - Line is title-cased and short (≤ 8 words)
        """
        if _RE_TRAILING_COLON.search(line):
            return True
        if _RE_ALL_CAPS.match(line):
            return True
        words = line.split()
        if len(words) <= 8 and _RE_TITLE_CASE_ISOLATED.match(line):
            return True
        return False
