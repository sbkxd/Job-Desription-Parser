"""Experience requirement extraction engine."""

import re

from app.extraction.schemas.schemas import ExperienceRequirement

# ---------------------------------------------------------------------------
# Regex Patterns for Experience Extraction
# ---------------------------------------------------------------------------

# Matches ranges: "2-4 years", "3 to 5 years", "2 - 5+ years"
_RE_RANGE = re.compile(
    r"\b(?:experience\s+of\s+)?(\d+)\s*(?:-|to)\s*(\d+)\+?\s*years?(?:\s+of)?\b",
    re.IGNORECASE,
)

# Matches lower bounds (min years): "3+ years", "minimum 5 years", "at least 3 years", "3 years or more"
_RE_MIN_BOUNDS = [
    re.compile(r"\b(\d+)\s*\+\s*years?\b", re.IGNORECASE),
    re.compile(
        r"\b(?:minimum|min|at\s+least|atleast|greater\s+than|more\s+than|over)\s+(\d+)\s*years?\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(\d+)\s*years?\s*(?:or\s+more|minimum|at\s+least)\b", re.IGNORECASE),
]

# Matches upper bounds (max years): "up to 5 years", "maximum 3 years", "under 4 years"
_RE_MAX_BOUNDS = [
    re.compile(
        r"\b(?:up\s+to|maximum|max|under|less\s+than)\s+(\d+)\s*years?\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(\d+)\s*years?\s*(?:maximum|max|limit)\b", re.IGNORECASE),
]

# Matches exact years: "5 years", "1 year"
_RE_EXACT = re.compile(r"\b(\d+)\s*years?\b", re.IGNORECASE)


class ExperienceExtractor:
    """Extracts minimum and maximum years of experience from segmented job description text."""

    def extract(self, sections: dict[str, list[str]]) -> ExperienceRequirement:
        """Extract experience bounds from document sections.

        Prioritizes the requirements section, falls back to responsibilities and other sections.
        """
        # Search sections in priority order
        search_order = ["requirements", "responsibilities", "other", "nice_to_have"]

        for sec_name in search_order:
            lines = sections.get(sec_name, [])
            for line in lines:
                req = self._extract_from_line(line)
                if req.min_years is not None or req.max_years is not None:
                    return req

        return ExperienceRequirement()

    def _extract_from_line(self, line: str) -> ExperienceRequirement:
        """Scan a single line of text to extract experience requirements."""
        # 1. Range Check (e.g. 2-4 years)
        m = _RE_RANGE.search(line)
        if m:
            return ExperienceRequirement(
                min_years=float(m.group(1)), max_years=float(m.group(2))
            )

        # 2. Min Bound Check (e.g. 3+ years)
        for pattern in _RE_MIN_BOUNDS:
            m = pattern.search(line)
            if m:
                return ExperienceRequirement(
                    min_years=float(m.group(1)), max_years=None
                )

        # 3. Max Bound Check (e.g. up to 5 years)
        for pattern in _RE_MAX_BOUNDS:
            m = pattern.search(line)
            if m:
                return ExperienceRequirement(
                    min_years=None, max_years=float(m.group(1))
                )

        # 4. Exact Check (e.g. 5 years)
        m = _RE_EXACT.search(line)
        if m:
            val = float(m.group(1))
            return ExperienceRequirement(min_years=val, max_years=val)

        return ExperienceRequirement()
