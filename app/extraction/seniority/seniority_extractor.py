"""Seniority level extraction engine."""

import re

from app.extraction.schemas.schemas import ExperienceRequirement, SeniorityLevel

# Mapping keywords to canonical seniority strings
_SENIORITY_KEYWORDS = [
    ("Intern", ["intern", "internship", "co-op"]),
    ("Junior", ["junior", "jr", "entry level", "entry-level"]),
    ("Associate", ["associate"]),
    ("Senior", ["senior", "sr", "experienced"]),
    ("Lead", ["lead", "team lead", "tech lead"]),
    ("Staff", ["staff"]),
    ("Principal", ["principal"]),
    ("Manager", ["manager", "project manager", "product manager"]),
    ("Director", ["director", "head of", "vp"]),
]


class SeniorityExtractor:
    """Extracts seniority level (Senior, Mid, Junior, etc.) from job descriptions."""

    def extract(
        self,
        sections: dict[str, list[str]],
        experience: ExperienceRequirement | None = None,
    ) -> SeniorityLevel:
        """Extract seniority using title signals, text patterns, and experience years.

        Returns:
            SeniorityLevel with a confidence score.
        """
        # 1. Scan title / first few lines of document for explicit signals
        title_match = self._scan_title_signals(sections)
        if title_match:
            return title_match

        # 2. Scan full document content for keywords
        content_match = self._scan_content_keywords(sections)
        if content_match:
            return content_match

        # 3. Fallback to experience-based mapping
        if experience and experience.min_years is not None:
            return self._map_experience_fallback(experience.min_years)

        # Default fallback
        return SeniorityLevel(seniority="Mid", confidence=0.4)

    def _scan_title_signals(
        self, sections: dict[str, list[str]]
    ) -> SeniorityLevel | None:
        """Scan title and first few lines of document for explicit signals."""
        lines_to_scan = []
        if "other" in sections and sections["other"]:
            lines_to_scan.extend(sections["other"][:3])
        if "about_company" in sections and sections["about_company"]:
            lines_to_scan.extend(sections["about_company"][:2])

        for canon, keywords in _SENIORITY_KEYWORDS:
            for kw in keywords:
                pattern = rf"\b{kw}\b"
                for line in lines_to_scan:
                    if re.search(pattern, line, re.IGNORECASE):
                        return SeniorityLevel(seniority=canon, confidence=0.95)
        return None

    def _scan_content_keywords(
        self, sections: dict[str, list[str]]
    ) -> SeniorityLevel | None:
        """Scan full document content for keywords."""
        all_lines = []
        for lines in sections.values():
            all_lines.extend(lines)

        keyword_hits = {canon: 0 for canon, _ in _SENIORITY_KEYWORDS}
        for canon, keywords in _SENIORITY_KEYWORDS:
            for kw in keywords:
                pattern = rf"\b{kw}\b"
                for line in all_lines:
                    if re.search(pattern, line, re.IGNORECASE):
                        keyword_hits[canon] += 1

        best_canon = None
        max_hits = 0
        for canon, hits in keyword_hits.items():
            if hits > max_hits:
                max_hits = hits
                best_canon = canon

        if best_canon and max_hits > 0:
            return SeniorityLevel(seniority=best_canon, confidence=0.8)
        return None

    def _map_experience_fallback(self, min_y: float) -> SeniorityLevel:
        """Fallback to experience-based mapping."""
        if min_y >= 8:
            return SeniorityLevel(seniority="Principal", confidence=0.6)
        if min_y >= 6:
            return SeniorityLevel(seniority="Lead", confidence=0.6)
        if min_y >= 5:
            return SeniorityLevel(seniority="Senior", confidence=0.7)
        if min_y >= 2:
            return SeniorityLevel(seniority="Mid", confidence=0.7)
        if min_y >= 1:
            return SeniorityLevel(seniority="Junior", confidence=0.6)
        return SeniorityLevel(seniority="Intern", confidence=0.6)
