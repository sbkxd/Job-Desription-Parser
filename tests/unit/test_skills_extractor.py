from app.extraction.skills.skills_extractor import SkillsExtractor


def test_skills_extractor_gazetteer():
    extractor = SkillsExtractor()
    sections = {
        "requirements": ["Must have 3 years of Python and C++ experience."],
        "responsibilities": ["Develop REST APIs using Django and FastAPI."],
        "nice_to_have": ["Knowledge of Docker is a plus."],
    }

    skills = extractor.extract(sections)

    # Names of extracted skills (sorted in extractor._post_process)
    names = [s.name for s in skills]

    assert "Python" in names
    assert "C++" in names
    assert "REST" in names
    assert "Django" in names
    assert "FastAPI" in names
    assert "Docker" in names

    # Track sections
    python_mention = next(s for s in skills if s.name == "Python")
    assert python_mention.section == "requirements"

    django_mention = next(s for s in skills if s.name == "Django")
    assert django_mention.section == "responsibilities"


def test_skills_extractor_dedup():
    extractor = SkillsExtractor()
    # Python in multiple sections
    sections = {
        "requirements": ["Python expert needed."],
        "responsibilities": ["Writing python scripts daily."],
    }

    skills = extractor.extract(sections)
    names = [s.name for s in skills]

    # Python should only occur once
    assert names.count("Python") == 1
    # Should prefer 'requirements' section
    python_mention = next(s for s in skills if s.name == "Python")
    assert python_mention.section == "requirements"


def test_skills_version_handling():
    extractor = SkillsExtractor()
    sections = {
        "requirements": ["React and ReactJS developer needed."],
    }
    skills = extractor.extract(sections)
    names = [s.name for s in skills]

    # React and ReactJS should remain separate
    assert "React" in names
    assert "ReactJS" in names
