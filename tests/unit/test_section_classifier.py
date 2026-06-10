from app.preprocessing.classifiers.section_classifier import SectionClassifier
from app.preprocessing.schemas.schemas import SectionType


def test_section_classifier_heading_confidence():
    classifier = SectionClassifier()

    # High confidence heading pre-determined
    sec_type, conf = classifier.classify(
        heading="Responsibilities",
        lines=["Write some code"],
        detected_type=SectionType.RESPONSIBILITIES,
        heading_confidence=1.0,
    )
    assert sec_type == SectionType.RESPONSIBILITIES
    assert conf == 1.0


def test_section_classifier_content_heuristics():
    classifier = SectionClassifier()

    # Heading has low confidence or None, but content has strong keywords
    sec_type, conf = classifier.classify(
        heading="Some Title",
        lines=["We offer a competitive salary, gym benefits, and health insurance."],
        detected_type=None,
        heading_confidence=0.0,
    )
    assert sec_type == SectionType.BENEFITS
    assert conf >= 0.3

    sec_type, conf = classifier.classify(
        heading=None,
        lines=[
            "Must have 3 years of Python experience, BS degree, and SQL proficiency."
        ],
        detected_type=None,
        heading_confidence=0.0,
    )
    assert sec_type == SectionType.REQUIREMENTS
    assert conf >= 0.3


def test_section_classifier_fallback():
    classifier = SectionClassifier()

    # No heading, no content match
    sec_type, conf = classifier.classify(
        heading=None,
        lines=["Random text with no keywords."],
        detected_type=None,
        heading_confidence=0.0,
    )
    assert sec_type == SectionType.OTHER
    assert conf == 0.2
