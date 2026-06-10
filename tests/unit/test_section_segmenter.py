from app.preprocessing.schemas.schemas import SectionType
from app.preprocessing.segmenters.section_segmenter import SectionSegmenter


def test_segmentation_with_headings():
    segmenter = SectionSegmenter()

    lines = [
        "Preamble text about the job.",
        "Key Responsibilities",
        "Develop APIs",
        "Write tests",
        "Requirements",
        "Python skills",
    ]

    sections = segmenter.segment(lines)

    assert len(sections) == 3

    # Section 1: Preamble
    assert sections[0].heading is None
    assert sections[0].detected_type == SectionType.OTHER
    assert sections[0].lines == ["Preamble text about the job."]

    # Section 2: Responsibilities
    assert sections[1].heading == "Key Responsibilities"
    assert sections[1].detected_type == SectionType.RESPONSIBILITIES
    assert sections[1].lines == ["Develop APIs", "Write tests"]

    # Section 3: Requirements
    assert sections[2].heading == "Requirements"
    assert sections[2].detected_type == SectionType.REQUIREMENTS
    assert sections[2].lines == ["Python skills"]


def test_segmentation_no_headings():
    segmenter = SectionSegmenter()

    lines = [
        "This is a job posting.",
        "It has no headers at all.",
    ]

    sections = segmenter.segment(lines)

    assert len(sections) == 1
    assert sections[0].heading is None
    assert sections[0].detected_type == SectionType.OTHER
    assert sections[0].lines == lines
