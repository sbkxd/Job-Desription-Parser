from app.preprocessing.classifiers.boilerplate_detector import BoilerplateDetector
from app.preprocessing.schemas.schemas import BoilerplateCategory


def test_boilerplate_detection():
    detector = BoilerplateDetector()

    lines = [
        "Altrosyn is hiring.",
        "We are looking for a backend engineer.",
        "All qualified applicants will receive consideration for employment without regard to race, color, or religion.",
        "Must be authorized to work in the US.",
        "Please send your resume to jobs@altrosyn.com.",
        "We are an innovative fast-growing startup.",
        "Enjoy coding with us.",
    ]

    clean_lines, removed = detector.detect(lines)

    # Verify clean lines are retained
    assert "Altrosyn is hiring." in clean_lines
    assert "We are looking for a backend engineer." in clean_lines
    assert "Enjoy coding with us." in clean_lines

    # Verify boilerplate lines are removed
    assert (
        "All qualified applicants will receive consideration for employment without regard to race, color, or religion."
        not in clean_lines
    )
    assert "Please send your resume to jobs@altrosyn.com." not in clean_lines
    assert "We are an innovative fast-growing startup." not in clean_lines

    # Verify tracking in removed blocks
    categories = [block.category for block in removed]
    assert BoilerplateCategory.EQUAL_OPPORTUNITY in categories
    assert BoilerplateCategory.APPLICATION_INSTRUCTIONS in categories
    assert BoilerplateCategory.RECRUITMENT_MARKETING in categories


def test_short_lines_not_boilerplate():
    detector = BoilerplateDetector()
    # A short line matching a keyword shouldn't trigger, e.g. "Apply today!" (12 chars)
    # len("Apply today!") is 12, which is < 20 characters
    lines = ["Apply today!"]
    clean, removed = detector.detect(lines)
    assert len(clean) == 1
    assert len(removed) == 0
