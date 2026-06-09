"""Unit tests for Milestone 2.2 — Source Detection Engine."""

import pytest

from app.ingestion.detectors import SourceDetector, detector
from app.ingestion.schemas import SourceType


@pytest.fixture()
def det() -> SourceDetector:
    return SourceDetector()


# ---------------------------------------------------------------------------
# Known platform classification
# ---------------------------------------------------------------------------


class TestKnownPlatforms:
    @pytest.mark.parametrize(
        "url,expected",
        [
            # Naukri
            ("https://www.naukri.com/job-listings-python-developer", SourceType.NAUKRI),
            ("https://naukri.com/mnjuser/homepage", SourceType.NAUKRI),
            # Foundit
            ("https://www.foundit.in/job/python-engineer-123", SourceType.FOUNDIT),
            ("https://monsterindia.com/srp/results", SourceType.FOUNDIT),
            # Indeed
            ("https://in.indeed.com/viewjob?jk=abc123", SourceType.INDEED),
            ("https://www.indeed.com/job/software-engineer-abc", SourceType.INDEED),
            ("https://indeed.co.in/viewjob?jk=xyz", SourceType.INDEED),
            # Greenhouse
            ("https://boards.greenhouse.io/acme/jobs/12345", SourceType.GREENHOUSE),
            ("https://greenhouse.io/jobs/acme", SourceType.GREENHOUSE),
            # Lever
            ("https://jobs.lever.co/acme/abc-123", SourceType.LEVER),
            ("https://lever.co/company/role/abc", SourceType.LEVER),
            # Workable
            ("https://apply.workable.com/acme/j/abc123/", SourceType.WORKABLE),
            ("https://www.workable.com/job/abc123", SourceType.WORKABLE),
        ],
    )
    def test_known_platform_detection(
        self, det: SourceDetector, url: str, expected: SourceType
    ):
        assert det.detect(url) == expected


# ---------------------------------------------------------------------------
# Generic ATS detection
# ---------------------------------------------------------------------------


class TestGenericATS:
    @pytest.mark.parametrize(
        "url",
        [
            "https://company.com/careers/software-engineer-123",
            "https://hr.company.com/jobs/open-positions",
            "https://jobs.company.io/apply/senior-dev",
            "https://hiring.taleo.net/careersection/apply",
            "https://company.icims.com/jobs/123/job",
            "https://company.jobvite.com/position/engineer",
            "https://company.ashbyhq.com/job/123",
            "https://company.smartrecruiters.com/openings/senior-engineer",
        ],
    )
    def test_generic_ats_detection(self, det: SourceDetector, url: str):
        assert det.detect(url) == SourceType.GENERIC_ATS


# ---------------------------------------------------------------------------
# Unknown / edge cases
# ---------------------------------------------------------------------------


class TestUnknownAndEdgeCases:
    def test_empty_string(self, det: SourceDetector):
        assert det.detect("") == SourceType.UNKNOWN

    def test_none_like_empty(self, det: SourceDetector):
        # None passed as empty — tests defensive coding
        assert det.detect("   ") == SourceType.UNKNOWN

    def test_non_http_scheme(self, det: SourceDetector):
        assert det.detect("ftp://naukri.com/jobs/123") == SourceType.UNKNOWN

    def test_bare_domain(self, det: SourceDetector):
        assert det.detect("naukri.com/jobs/123") == SourceType.UNKNOWN

    def test_random_https_url(self, det: SourceDetector):
        assert det.detect("https://randomsite.xyz/blog/post-1") == SourceType.UNKNOWN

    def test_malformed_url_with_http_prefix(self, det: SourceDetector):
        # Malformed but starts with http — should not crash
        result = det.detect("https://")
        assert result == SourceType.UNKNOWN

    def test_linkedin_is_generic_ats(self, det: SourceDetector):
        """LinkedIn job URLs match the generic /jobs/ ATS pattern."""
        result = det.detect("https://www.linkedin.com/jobs/view/12345")
        assert result == SourceType.GENERIC_ATS

    def test_non_job_linkedin_is_unknown(self, det: SourceDetector):
        """LinkedIn profile pages are unknown."""
        result = det.detect("https://www.linkedin.com/in/john-doe")
        assert result == SourceType.UNKNOWN


# ---------------------------------------------------------------------------
# Requires JavaScript
# ---------------------------------------------------------------------------


class TestRequiresJavaScript:
    @pytest.mark.parametrize(
        "source_type,expected",
        [
            (SourceType.GREENHOUSE, True),
            (SourceType.LEVER, True),
            (SourceType.WORKABLE, True),
            (SourceType.NAUKRI, False),
            (SourceType.FOUNDIT, False),
            (SourceType.INDEED, False),
            (SourceType.GENERIC_ATS, False),
            (SourceType.PDF, False),
            (SourceType.UNKNOWN, False),
        ],
    )
    def test_js_requirement(
        self, det: SourceDetector, source_type: SourceType, expected: bool
    ):
        assert det.requires_javascript(source_type) == expected


# ---------------------------------------------------------------------------
# Is Supported
# ---------------------------------------------------------------------------


class TestIsSupported:
    def test_known_platforms_supported(self, det: SourceDetector):
        for st in [
            SourceType.NAUKRI,
            SourceType.FOUNDIT,
            SourceType.INDEED,
            SourceType.GREENHOUSE,
            SourceType.LEVER,
            SourceType.WORKABLE,
            SourceType.GENERIC_ATS,
            SourceType.PDF,
        ]:
            assert det.is_supported(st) is True

    def test_unknown_not_supported(self, det: SourceDetector):
        assert det.is_supported(SourceType.UNKNOWN) is False


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------


def test_module_singleton_works():
    result = detector.detect("https://jobs.lever.co/acme/123")
    assert result == SourceType.LEVER
