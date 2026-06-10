import pytest
from pydantic import ValidationError

from app.extraction.schemas.schemas import (
    ExperienceRequirement,
    ExtractionResult,
    RequirementClassification,
    SeniorityLevel,
    SkillMention,
)


def test_extraction_schemas_validation():
    # SkillMention
    skill = SkillMention(name="Python", confidence=0.9, section="requirements")
    assert skill.name == "Python"
    assert skill.confidence == 0.9
    assert skill.section == "requirements"

    with pytest.raises(ValidationError):
        # confidence out of range
        SkillMention(name="Python", confidence=1.2, section="requirements")

    # ExperienceRequirement
    exp = ExperienceRequirement(min_years=2.0, max_years=5.0)
    assert exp.min_years == 2.0
    assert exp.max_years == 5.0

    # SeniorityLevel
    seniority = SeniorityLevel(seniority="Senior", confidence=0.95)
    assert seniority.seniority == "Senior"
    assert seniority.confidence == 0.95

    # RequirementClassification
    req = RequirementClassification(
        text="Must have Python", classification="Required", confidence=0.95
    )
    assert req.text == "Must have Python"
    assert req.classification == "Required"
    assert req.confidence == 0.95

    # ExtractionResult
    result = ExtractionResult(
        success=True,
        skills=[skill],
        experience=exp,
        seniority=seniority,
        requirements_classification=[req],
        duration_ms=12.5,
    )
    assert result.success is True
    assert len(result.skills) == 1
    assert result.experience.min_years == 2.0
    assert result.seniority.seniority == "Senior"
    assert len(result.requirements_classification) == 1
    assert result.duration_ms == 12.5
