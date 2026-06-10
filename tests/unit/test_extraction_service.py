import json
import os

from app.extraction.services.extraction_service import ExtractionService

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "fixtures", "extraction"
)


def test_extraction_service_basic():
    service = ExtractionService()
    doc = {
        "responsibilities": ["Develop REST APIs in Python."],
        "requirements": ["Must have 3 years experience.", "FastAPI knowledge."],
    }
    result = service.extract(doc)
    assert result.success is True
    assert len(result.skills) > 0
    assert result.experience.min_years == 3.0
    assert result.duration_ms is not None


def test_extraction_service_error():
    service = ExtractionService()
    # Passing invalid object type should raise exception and return success=False
    result = service.extract(None)  # type: ignore
    assert result.success is False
    assert result.error is not None


def test_extraction_fixtures():
    service = ExtractionService()
    roles = [
        "software_engineer",
        "data_scientist",
        "ml_engineer",
        "backend_engineer",
        "frontend_engineer",
    ]

    for role in roles:
        input_path = os.path.join(FIXTURE_DIR, f"{role}_input.json")
        expected_path = os.path.join(FIXTURE_DIR, f"{role}_expected.json")

        assert os.path.exists(input_path), f"Input file {input_path} missing"
        assert os.path.exists(expected_path), f"Expected file {expected_path} missing"

        with open(input_path, "r", encoding="utf-8") as f:
            input_doc = json.load(f)

        with open(expected_path, "r", encoding="utf-8") as f:
            expected_output = json.load(f)

        result = service.extract(input_doc)
        assert result.success is True

        # Check Skills
        actual_skills = sorted(
            [s.model_dump() for s in result.skills], key=lambda x: x["name"]
        )
        expected_skills = sorted(expected_output["skills"], key=lambda x: x["name"])
        assert len(actual_skills) == len(
            expected_skills
        ), f"Skill count mismatch for {role}"
        for act, exp in zip(actual_skills, expected_skills, strict=False):
            assert act["name"] == exp["name"]
            assert act["section"] == exp["section"]

        # Check Experience
        assert (
            result.experience.min_years == expected_output["experience"]["min_years"]
        ), f"Min years mismatch for {role}"
        assert (
            result.experience.max_years == expected_output["experience"]["max_years"]
        ), f"Max years mismatch for {role}"

        # Check Seniority
        assert result.seniority is not None
        assert (
            result.seniority.seniority == expected_output["seniority"]["seniority"]
        ), f"Seniority mismatch for {role}"

        # Check Requirements Classifications
        actual_reqs = [r.model_dump() for r in result.requirements_classification]
        expected_reqs = expected_output["requirements_classification"]
        assert len(actual_reqs) == len(
            expected_reqs
        ), f"Requirement count mismatch for {role}"
        for act, exp in zip(actual_reqs, expected_reqs, strict=False):
            assert act["text"] == exp["text"]
            assert act["classification"] == exp["classification"]
