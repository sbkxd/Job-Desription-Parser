from app.extraction.schemas.schemas import ExperienceRequirement
from app.extraction.seniority.seniority_extractor import SeniorityExtractor


def test_seniority_extractor_keywords():
    extractor = SeniorityExtractor()

    # Match in title section (other)
    sections = {
        "other": ["Senior Software Engineer"],
    }
    res = extractor.extract(sections)
    assert res.seniority == "Senior"
    assert res.confidence == 0.95

    # Match in body
    sections = {
        "responsibilities": ["Work as a junior developer on teams."],
    }
    res = extractor.extract(sections)
    assert res.seniority == "Junior"
    assert res.confidence == 0.8


def test_seniority_extractor_experience_fallback():
    extractor = SeniorityExtractor()

    # No title/keywords, fallback to min years
    sections = {}
    exp = ExperienceRequirement(min_years=6.0)
    res = extractor.extract(sections, experience=exp)
    assert res.seniority == "Lead"
    assert res.confidence == 0.6

    exp = ExperienceRequirement(min_years=3.0)
    res = extractor.extract(sections, experience=exp)
    assert res.seniority == "Mid"
    assert res.confidence == 0.7
