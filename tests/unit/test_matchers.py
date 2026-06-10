"""Unit tests for string cleaning and specific skill matching algorithms."""

from app.normalization.matchers.alias_matcher import AliasMatcher
from app.normalization.matchers.embedding_matcher import EmbeddingMatcher
from app.normalization.matchers.exact_matcher import ExactMatcher
from app.normalization.matchers.fuzzy_matcher import FuzzyMatcher
from app.normalization.matchers.preprocess import clean_skill_name
from app.normalization.taxonomy.taxonomy_repository import TaxonomyRepository


def test_clean_skill_name() -> None:
    assert clean_skill_name("React.js") == "react"
    assert clean_skill_name("ReactJS") == "react"
    assert clean_skill_name("React JS") == "react"
    assert clean_skill_name("Node.js") == "node"
    assert clean_skill_name("PostgreSQL") == "postgresql"
    assert clean_skill_name("  Python 3  ") == "python3"
    assert clean_skill_name("CI/CD") == "cicd"


def test_exact_matcher() -> None:
    repo = TaxonomyRepository()
    matcher = ExactMatcher(repo)

    res = matcher.match("Python")
    assert res is not None
    assert res.esco_skill.name == "Python"
    assert res.score == 1.0
    assert res.match_method == "exact"

    # Fails on aliases
    assert matcher.match("ReactJS") is None


def test_alias_matcher() -> None:
    repo = TaxonomyRepository()
    matcher = AliasMatcher(repo)

    res = matcher.match("ReactJS")
    assert res is not None
    assert res.esco_skill.name == "React"
    assert res.score == 0.95
    assert res.match_method == "alias"

    res = matcher.match("Postgres")
    assert res is not None
    assert res.esco_skill.name == "PostgreSQL"


def test_fuzzy_matcher() -> None:
    repo = TaxonomyRepository()
    matcher = FuzzyMatcher(repo, threshold=80)

    res = matcher.match("Tensor Flow")
    assert res is not None
    assert res.esco_skill.name == "TensorFlow"
    assert res.score >= 0.8
    assert res.match_method == "fuzzy"


def test_embedding_matcher() -> None:
    repo = TaxonomyRepository()
    matcher = EmbeddingMatcher(repo, threshold=0.5)

    res = matcher.match("Deep Learning Models")
    assert res is not None
    assert res.esco_skill.name == "Deep Learning"
    assert res.score >= 0.5
    assert res.match_method == "embedding"
