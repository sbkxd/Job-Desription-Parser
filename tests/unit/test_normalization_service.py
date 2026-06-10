"""Integration and validation tests for the SkillNormalizationService using fixtures."""

import json
import os

from app.normalization.services.normalization_service import SkillNormalizationService

FIXTURE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "fixtures",
    "normalization",
    "skills_fixtures.json",
)


def test_normalization_service_runs_successfully() -> None:
    service = SkillNormalizationService()
    res = service.normalize(["ReactJS", "python", "UnknownSkill"])

    assert len(res.normalized_skills) == 3

    # Check ReactJS alias mapping
    react_match = next(s for s in res.normalized_skills if s.raw_skill == "ReactJS")
    assert react_match.normalized_skill == "React"
    assert react_match.esco_id == "esco_react"
    assert react_match.match_method == "alias"
    assert react_match.confidence == 0.95

    # Check python exact mapping
    python_match = next(s for s in res.normalized_skills if s.raw_skill == "python")
    assert python_match.normalized_skill == "Python"
    assert python_match.esco_id == "esco_python"
    assert python_match.match_method == "exact"
    assert python_match.confidence == 1.0

    # Check unmapped skill fallback
    unmapped_match = next(
        s for s in res.normalized_skills if s.raw_skill == "UnknownSkill"
    )
    assert unmapped_match.normalized_skill == "UnknownSkill"
    assert unmapped_match.esco_id == "unmapped"
    assert unmapped_match.match_method == "none"
    assert unmapped_match.confidence == 0.0


def test_normalization_fixtures_validation() -> None:
    """Validate all skills from the gold-standard fixture dataset."""
    assert os.path.exists(
        FIXTURE_PATH
    ), f"Normalization fixture file missing at {FIXTURE_PATH}"

    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    service = SkillNormalizationService()
    raw_inputs = [item["raw_skill"] for item in fixtures]

    res = service.normalize(raw_inputs)
    assert len(res.normalized_skills) == len(fixtures)

    for item in fixtures:
        actual_match = next(
            s for s in res.normalized_skills if s.raw_skill == item["raw_skill"]
        )
        assert (
            actual_match.normalized_skill == item["expected_normalized"]
        ), f"Normalized name mismatch for raw skill: {item['raw_skill']}"
        assert (
            actual_match.esco_id == item["expected_esco_id"]
        ), f"ESCO ID mismatch for raw skill: {item['raw_skill']}"
