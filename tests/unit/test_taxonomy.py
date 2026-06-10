"""Unit tests for ESCO taxonomy loader and repository indexing."""

import pytest

from app.normalization.loaders.taxonomy_loader import TaxonomyLoader
from app.normalization.taxonomy.taxonomy_repository import TaxonomyRepository


def test_taxonomy_loader() -> None:
    loader = TaxonomyLoader()
    skills = loader.load()
    assert len(skills) > 0
    # Check that a standard skill like Python is loaded correctly
    python_skill = next(s for s in skills if s.name == "Python")
    assert python_skill.esco_id == "esco_python"
    assert "python" in python_skill.alternative_labels


def test_taxonomy_loader_file_not_found() -> None:
    loader = TaxonomyLoader(dataset_path="non_existent_file.json")
    with pytest.raises(FileNotFoundError):
        loader.load()


def test_taxonomy_repository_singleton_and_indexing() -> None:
    repo1 = TaxonomyRepository()
    repo2 = TaxonomyRepository()

    # Assert singleton behavior
    assert repo1 is repo2

    # Check exact index
    skill = repo1.find_exact("python")
    assert skill is not None
    assert skill.name == "Python"
    assert skill.esco_id == "esco_python"

    # Check alias index
    skill_alias = repo1.find_alias("reactjs")
    assert skill_alias is not None
    assert skill_alias.name == "React"

    # Check embedding matrix retrieval
    matrix, skills_list = repo1.get_embeddings_matrix()
    assert matrix is not None
    assert len(skills_list) == len(repo1.get_all_skills())
    assert matrix.shape[0] == len(skills_list)
