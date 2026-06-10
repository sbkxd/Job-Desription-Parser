"""Unit tests for Skill Normalization schemas."""

from app.normalization.schemas.schemas import (
    EscoSkill,
    MatchResult,
    NormalizationResult,
    NormalizedSkill,
    RawSkill,
    SkillCandidate,
)


def test_raw_skill_validation() -> None:
    skill = RawSkill(name="Python", confidence=0.92)
    assert skill.name == "Python"
    assert skill.confidence == 0.92


def test_esco_skill_validation() -> None:
    skill = EscoSkill(
        esco_id="esco_python",
        name="Python",
        description="A programming language.",
        alternative_labels=["python3"],
    )
    assert skill.esco_id == "esco_python"
    assert skill.name == "Python"
    assert skill.description == "A programming language."
    assert "python3" in skill.alternative_labels


def test_skill_candidate_validation() -> None:
    esco_sk = EscoSkill(esco_id="1", name="React", alternative_labels=[])
    cand = SkillCandidate(esco_skill=esco_sk, score=0.95, match_method="alias")
    assert cand.esco_skill.name == "React"
    assert cand.score == 0.95
    assert cand.match_method == "alias"


def test_normalized_skill_validation() -> None:
    norm = NormalizedSkill(
        raw_skill="ReactJS",
        normalized_skill="React",
        esco_id="1",
        confidence=0.95,
        match_method="alias",
    )
    assert norm.raw_skill == "ReactJS"
    assert norm.normalized_skill == "React"
    assert norm.esco_id == "1"
    assert norm.confidence == 0.95
    assert norm.match_method == "alias"


def test_match_result_validation() -> None:
    esco_sk = EscoSkill(esco_id="1", name="React", alternative_labels=[])
    cand = SkillCandidate(esco_skill=esco_sk, score=0.95, match_method="alias")
    res = MatchResult(raw_skill="ReactJS", candidates=[cand])
    assert res.raw_skill == "ReactJS"
    assert len(res.candidates) == 1
    assert res.candidates[0].esco_skill.name == "React"


def test_normalization_result_validation() -> None:
    norm = NormalizedSkill(
        raw_skill="ReactJS",
        normalized_skill="React",
        esco_id="1",
        confidence=0.95,
        match_method="alias",
    )
    res = NormalizationResult(normalized_skills=[norm])
    assert len(res.normalized_skills) == 1
    assert res.normalized_skills[0].raw_skill == "ReactJS"
