import pytest
from pydantic import ValidationError

from app.preprocessing.schemas.schemas import (
    BoilerplateBlock,
    BoilerplateCategory,
    RawDocument,
    Section,
    SectionType,
    SegmentedDocument,
)


def test_section_type_enum():
    assert SectionType.RESPONSIBILITIES == "responsibilities"
    assert SectionType.OTHER == "other"


def test_raw_document_validation():
    doc = RawDocument(raw_text="Some job info", source_type="naukri")
    assert doc.raw_text == "Some job info"
    assert doc.source_type == "naukri"

    with pytest.raises(ValidationError):
        RawDocument(raw_text="")

    with pytest.raises(ValidationError):
        RawDocument(raw_text="   ")


def test_section_properties():
    sec = Section(
        section_type=SectionType.RESPONSIBILITIES,
        heading="Job Duties",
        lines=["Do task A", "Do task B"],
        confidence=0.9,
    )
    assert sec.text == "Do task A\nDo task B"
    assert not sec.is_empty

    empty_sec = Section(section_type=SectionType.OTHER, lines=["", "  "])
    assert empty_sec.is_empty


def test_segmented_document():
    sec1 = Section(
        section_type=SectionType.RESPONSIBILITIES,
        heading="Duties",
        lines=["Task 1"],
    )
    sec2 = Section(
        section_type=SectionType.REQUIREMENTS,
        heading="Skills",
        lines=["Skill 1"],
    )
    doc = SegmentedDocument(
        sections=[sec1, sec2],
        boilerplate_removed=[
            BoilerplateBlock(
                category=BoilerplateCategory.EQUAL_OPPORTUNITY,
                lines=["EEO statement"],
            )
        ],
    )
    assert len(doc.get_sections(SectionType.RESPONSIBILITIES)) == 1
    assert doc.get_sections(SectionType.RESPONSIBILITIES)[0].lines == ["Task 1"]

    out = doc.to_output()
    assert out["responsibilities"] == ["Task 1"]
    assert out["requirements"] == ["Skill 1"]
    assert out["nice_to_have"] == []
