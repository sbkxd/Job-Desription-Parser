"""Source detection engine — classifies URLs to known job platforms."""

import re
from urllib.parse import urlparse

from app.ingestion.schemas import SourceType

# Platform classification rules: ordered list of (SourceType, domain patterns)
_PLATFORM_RULES: list[tuple[SourceType, list[str]]] = [
    (
        SourceType.NAUKRI,
        [r"naukri\.com"],
    ),
    (
        SourceType.FOUNDIT,
        [r"foundit\.in", r"monster\.com", r"monsterindia\.com"],
    ),
    (
        SourceType.INDEED,
        [r"indeed\.com", r"indeed\.co\.in"],
    ),
    (
        SourceType.GREENHOUSE,
        [r"greenhouse\.io", r"boards\.greenhouse\.io"],
    ),
    (
        SourceType.LEVER,
        [r"lever\.co", r"jobs\.lever\.co"],
    ),
    (
        SourceType.WORKABLE,
        [r"workable\.com", r"apply\.workable\.com"],
    ),
]

# Generic ATS path heuristics (applied after domain matching fails)
_GENERIC_ATS_PATH_PATTERNS: list[str] = [
    r"/careers/",
    r"/jobs/",
    r"/job-posting/",
    r"/apply/",
    r"/openings/",
    r"/positions/",
    r"/vacancies/",
    r"taleo\.net",
    r"icims\.com",
    r"successfactors\.com",
    r"brassring\.com",
    r"jobvite\.com",
    r"smartrecruiters\.com",
    r"ashbyhq\.com",
    r"rippling\.com",
]


def _extract_netloc(url: str) -> str:
    """Return the netloc (host) from a URL, lower-cased."""
    try:
        parsed = urlparse(url)
        return (parsed.netloc or "").lower()
    except Exception:
        return ""


def _extract_full_url_lower(url: str) -> str:
    """Return the full URL lower-cased for path/query matching."""
    return url.lower()


class SourceDetector:
    """
    Classifies a URL to a known SourceType.

    Resolution order:
    1. Known platform domain matching (exact hostname pattern).
    2. Generic ATS heuristics (path/domain patterns).
    3. Falls back to UNKNOWN.
    """

    def detect(self, url: str) -> SourceType:
        """
        Detect the platform for a given URL string.

        Args:
            url: The raw URL string to classify.

        Returns:
            SourceType enum value.
        """
        if not url or not isinstance(url, str):
            return SourceType.UNKNOWN

        url = url.strip()

        # Reject clearly non-HTTP URLs
        if not url.startswith(("http://", "https://")):
            return SourceType.UNKNOWN

        netloc = _extract_netloc(url)
        full = _extract_full_url_lower(url)

        # Step 1: Exact platform matching
        for platform, patterns in _PLATFORM_RULES:
            for pattern in patterns:
                if re.search(pattern, netloc):
                    return platform

        # Step 2: Generic ATS heuristics
        for pattern in _GENERIC_ATS_PATH_PATTERNS:
            if re.search(pattern, full):
                return SourceType.GENERIC_ATS

        return SourceType.UNKNOWN

    def detect_from_netloc(self, netloc: str) -> SourceType:
        """Detect from just the hostname/netloc portion."""
        for platform, patterns in _PLATFORM_RULES:
            for pattern in patterns:
                if re.search(pattern, netloc.lower()):
                    return platform
        return SourceType.UNKNOWN

    def requires_javascript(self, source_type: SourceType) -> bool:
        """
        Return True if this platform typically requires JS rendering.

        Platforms known to use heavy JS rendering:
        - Greenhouse: dynamic via React
        - Lever: dynamic via React
        - Workable: dynamic ATS
        """
        return source_type in {
            SourceType.GREENHOUSE,
            SourceType.LEVER,
            SourceType.WORKABLE,
        }

    def is_supported(self, source_type: SourceType) -> bool:
        """Return True if the platform is explicitly supported."""
        return source_type not in {SourceType.UNKNOWN}


# Module-level singleton
detector = SourceDetector()
