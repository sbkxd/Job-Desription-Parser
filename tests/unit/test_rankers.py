"""Unit tests for the Candidate Ranker and confidence scoring engine."""

from app.normalization.rankers.candidate_ranker import CandidateRanker
from app.normalization.schemas.schemas import EscoSkill, SkillCandidate


def test_candidate_ranker_priority() -> None:
    ranker = CandidateRanker()

    skill_react = EscoSkill(esco_id="1", name="React")
    skill_angular = EscoSkill(esco_id="2", name="Angular")

    cand_fuzzy = SkillCandidate(
        esco_skill=skill_react, score=0.88, match_method="fuzzy"
    )
    cand_alias = SkillCandidate(
        esco_skill=skill_angular, score=0.95, match_method="alias"
    )

    # Alias should win over Fuzzy despite similar scores
    res = ranker.rank("ReactJS", [cand_fuzzy, cand_alias])
    assert res is not None
    assert res.normalized_skill == "Angular"
    assert res.confidence == 0.95
    assert res.match_method == "alias"


def test_candidate_ranker_tie_resolution() -> None:
    ranker = CandidateRanker()

    skill1 = EscoSkill(esco_id="1", name="React Native")
    skill2 = EscoSkill(esco_id="2", name="React")

    cand1 = SkillCandidate(esco_skill=skill1, score=0.8, match_method="embedding")
    cand2 = SkillCandidate(esco_skill=skill2, score=0.8, match_method="embedding")

    # Tie should be resolved by choosing the shorter canonical name (React)
    res = ranker.rank("ReactJS", [cand1, cand2])
    assert res is not None
    assert res.normalized_skill == "React"


def test_candidate_ranker_empty_input() -> None:
    ranker = CandidateRanker()
    assert ranker.rank("Python", []) is None
