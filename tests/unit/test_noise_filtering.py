"""Unit and integration tests for JD noise filtering and section purification."""

import json
import os

import pytest

from app.preprocessing.noise.classifiers import ContentTypeClassifier
from app.preprocessing.noise.patterns import patterns
from app.preprocessing.noise.rules import (
    AtsArtifactRule,
    ContactInfoRule,
    LinkedInArtifactRule,
)
from app.preprocessing.noise.services import NoiseFilterService
from app.preprocessing.noise.validators import SectionPurifier
from app.preprocessing.schemas.schemas import RawDocument, Section
from app.preprocessing.services.segmentation_service import SegmentationService


@pytest.fixture
def noise_fixtures():
    """Load noise filtering fixtures."""
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "fixtures",
        "noise_filtering",
        "noise_fixtures.json",
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_regex_patterns():
    """Verify regex patterns for emails, phones, and URLs match correctly."""
    assert patterns.EMAIL_PATTERN.search("contact info@example.com here") is not None
    assert patterns.EMAIL_PATTERN.search("janedoe@umkc.edu") is not None
    assert patterns.EMAIL_PATTERN.search("not_an_email") is None

    assert patterns.PHONE_PATTERN.search("Call (816)235-0000 now") is not None
    assert patterns.PHONE_PATTERN.search("1-555-555-5555") is not None

    assert patterns.URL_PATTERN.search("Visit https://example.com/careers") is not None


def test_rules():
    """Verify concrete NoiseRules identify noise types."""
    contact_rule = ContactInfoRule()
    assert contact_rule.evaluate("janedoe@umkc.edu")["is_noise"] is True
    assert contact_rule.evaluate("(816)235-0000")["is_noise"] is True
    assert contact_rule.evaluate("Develop API endpoints")["is_noise"] is False

    ats_rule = AtsArtifactRule()
    assert ats_rule.evaluate("This section auto-populates")["is_noise"] is True
    assert ats_rule.evaluate("Select one of the following")["is_noise"] is True
    assert ats_rule.evaluate("Choose an option")["is_noise"] is True
    assert ats_rule.evaluate("Python experience required")["is_noise"] is False

    linkedin_rule = LinkedInArtifactRule()
    assert linkedin_rule.evaluate("People also viewed")["is_noise"] is True
    assert linkedin_rule.evaluate("Referrals increase your chances")["is_noise"] is True
    assert linkedin_rule.evaluate("Apply now")["is_noise"] is True
    assert (
        linkedin_rule.evaluate("Collaborate with cross-functional teams")["is_noise"]
        is False
    )


def test_content_classifier():
    """Verify ContentTypeClassifier categorizes lines correctly."""
    classifier = ContentTypeClassifier()
    assert classifier.classify_line("janedoe@umkc.edu") == "CONTACT_INFO"
    assert classifier.classify_line("Employment Type") == "METADATA"
    assert classifier.classify_line("This section auto-populates") == "NOISE"
    assert classifier.classify_line("Bachelor's degree in CS") == "EDUCATION"
    assert classifier.classify_line("Health insurance and 401k") == "BENEFIT"
    assert classifier.classify_line("Python experience") == "SKILL"
    assert classifier.classify_line("Develop new features") == "RESPONSIBILITY"


def test_noise_filter_service(noise_fixtures):
    """Verify NoiseFilterService purges noise lines and counts metrics."""
    service = NoiseFilterService()

    # Test LinkedIn Noisy JD
    linkedin_data = noise_fixtures["noisy_linkedin_jd"]
    lines = [ln.strip() for ln in linkedin_data["raw_text"].split("\n")]
    filtered, metrics = service.filter_noise(
        lines, source_type=linkedin_data["source_type"]
    )

    assert metrics["removed_lines"] == linkedin_data["expected_removed_lines"]
    assert "Apply Now" not in [ln.strip() for ln in filtered]
    assert "janedoe@umkc.edu" not in [ln.strip() for ln in filtered]


def test_segmentation_integration(noise_fixtures):
    """Verify complete segmentation service cleans and purges noise correctly."""
    seg_service = SegmentationService()

    # E2E Test: Noisy LinkedIn JD
    linkedin_data = noise_fixtures["noisy_linkedin_jd"]
    raw_doc = RawDocument(
        raw_text=linkedin_data["raw_text"],
        source_type=linkedin_data["source_type"],
    )
    result = seg_service.segment(raw_doc)
    assert result.success is True

    doc = result.document
    assert (
        doc.metadata["noise_removed_lines"] == linkedin_data["expected_removed_lines"]
    )

    # Verify Responsibilities section is sanitized
    resp_section = next(
        (s for s in doc.sections if s.section_type == "responsibilities"), None
    )
    assert resp_section is not None
    assert "janedoe@umkc.edu" not in resp_section.lines
    assert "(816)235-0000" not in resp_section.lines

    # Quality metrics check
    quality_scores = doc.metadata["section_quality_scores"]
    assert "responsibilities" in quality_scores
    assert (
        quality_scores["responsibilities"]["quality"]
        == linkedin_data["expected_responsibility_quality"]
    )


def test_section_purifier():
    """Verify SectionPurifier directly filters noise lines inside sections and scores them."""
    purifier = SectionPurifier()
    sections = [
        Section(
            section_type="responsibilities",
            heading="Responsibilities",
            lines=[
                "Develop clean code.",
                "janedoe@umkc.edu",  # Noise (email)
                "Build API interfaces.",
                "Employment Type",  # Noise (metadata)
            ],
            confidence=1.0,
        )
    ]
    purified, scores = purifier.purify_sections(sections)
    assert len(purified) == 1
    assert len(purified[0].lines) == 2
    assert "janedoe@umkc.edu" not in purified[0].lines
    assert "Employment Type" not in purified[0].lines
    assert scores["responsibilities"]["quality"] == 0.5
