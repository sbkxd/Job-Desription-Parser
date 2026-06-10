from app.extraction.requirements.requirement_classifier import RequirementClassifier


def test_requirement_classifier_keywords():
    classifier = RequirementClassifier()

    # Required
    res = classifier.classify_line("Must have 3 years of Python")
    assert res.classification == "Required"
    assert res.confidence == 0.95

    # Preferred
    res = classifier.classify_line("Experience with Docker preferred")
    assert res.classification == "Preferred"
    assert res.confidence == 0.95

    # Optional
    res = classifier.classify_line("Nice to have AWS experience")
    assert res.classification == "Optional"
    assert res.confidence == 0.95


def test_requirement_classifier_default():
    classifier = RequirementClassifier()

    # No keywords matching, default based on section context
    res = classifier.classify_line(
        "Understand relational databases", default_classification="Required"
    )
    assert res.classification == "Required"
    assert res.confidence == 0.7

    res = classifier.classify_line(
        "Understand relational databases", default_classification="Optional"
    )
    assert res.classification == "Optional"
    assert res.confidence == 0.7


def test_requirement_classifier_full():
    classifier = RequirementClassifier()
    sections = {
        "requirements": ["Must have Python.", "Knowledge of Docker."],
        "nice_to_have": ["AWS experience preferred.", "Kubernetes knowledge."],
    }

    results = classifier.classify(sections)
    assert len(results) == 4

    assert results[0].classification == "Required"  # Must
    assert results[1].classification == "Required"  # Default (requirements)
    assert results[2].classification == "Preferred"  # Preferred
    assert results[3].classification == "Optional"  # Default (nice_to_have)
