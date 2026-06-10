from app.extraction.experience.experience_extractor import ExperienceExtractor


def test_experience_extractor_ranges():
    extractor = ExperienceExtractor()

    # Range
    res = extractor._extract_from_line("Requires 2-4 years experience")
    assert res.min_years == 2.0
    assert res.max_years == 4.0

    res = extractor._extract_from_line("3 to 5+ years of programming")
    assert res.min_years == 3.0
    assert res.max_years == 5.0


def test_experience_extractor_min_bounds():
    extractor = ExperienceExtractor()

    # Plus notation
    res = extractor._extract_from_line("3+ years of experience")
    assert res.min_years == 3.0
    assert res.max_years is None

    # Minimum wording
    res = extractor._extract_from_line("Minimum 5 years of industry experience")
    assert res.min_years == 5.0
    assert res.max_years is None

    # At least wording
    res = extractor._extract_from_line("Requires at least 2 years in Python")
    assert res.min_years == 2.0
    assert res.max_years is None


def test_experience_extractor_max_bounds():
    extractor = ExperienceExtractor()

    # Up to
    res = extractor._extract_from_line("Up to 3 years experience required")
    assert res.min_years is None
    assert res.max_years == 3.0


def test_experience_extractor_exact():
    extractor = ExperienceExtractor()

    # Exact year
    res = extractor._extract_from_line("We need 5 years experience")
    assert res.min_years == 5.0
    assert res.max_years == 5.0


def test_experience_extractor_priority():
    extractor = ExperienceExtractor()
    sections = {
        "responsibilities": ["3 years experience"],
        "requirements": ["5+ years experience"],
    }
    # Should prioritize requirements over responsibilities
    res = extractor.extract(sections)
    assert res.min_years == 5.0
    assert res.max_years is None
