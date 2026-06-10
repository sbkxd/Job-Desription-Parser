from app.preprocessing.schemas.schemas import SectionType
from app.preprocessing.segmenters.heading_detector import HeadingDetector


def test_heading_detector_exact_aliases():
    detector = HeadingDetector()

    assert detector.is_heading("Key Responsibilities")
    assert detector.is_heading("What you will do:")
    assert detector.is_heading("Education & Experience")

    sec_type, conf = detector.classify_heading("Key Responsibilities")
    assert sec_type == SectionType.RESPONSIBILITIES
    assert conf == 1.0


def test_heading_detector_fuzzy_aliases():
    detector = HeadingDetector()

    # Slightly modified heading
    assert detector.is_heading("Key Responsibility")
    sec_type, conf = detector.classify_heading("Key Responsibility")
    assert sec_type == SectionType.RESPONSIBILITIES
    assert conf >= 0.82


def test_heading_detector_heuristics():
    detector = HeadingDetector()

    # Title-cased with colon
    assert detector.is_heading("Some Random Heading:")
    sec_type, conf = detector.classify_heading("Some Random Heading:")
    assert sec_type is None  # resolved to None by detector (structural only)
    assert conf == 0.5

    # All-caps line
    assert detector.is_heading("WHO WE ARE")
    sec_type, conf = detector.classify_heading("WHO WE ARE")
    # WHO WE ARE is in our alias table so it matches SectionType.ABOUT_COMPANY with high confidence
    assert sec_type == SectionType.ABOUT_COMPANY

    # An unknown all-caps heading
    assert detector.is_heading("UNEXPECTED HEADING LINE")
    sec_type, conf = detector.classify_heading("UNEXPECTED HEADING LINE")
    assert sec_type is None
    assert conf == 0.5


def test_not_headings():
    detector = HeadingDetector()

    # Too long
    assert not detector.is_heading(
        "This is a very long sentence describing what a backend developer does day to day."
    )
    # Empty
    assert not detector.is_heading("")
    assert not detector.is_heading("   ")
