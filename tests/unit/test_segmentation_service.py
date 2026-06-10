import json
import os

from app.preprocessing.schemas.schemas import RawDocument
from app.preprocessing.services.segmentation_service import SegmentationService

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "fixtures", "segmentation"
)


def test_segmentation_service_basic():
    service = SegmentationService()
    doc = RawDocument(raw_text="About Altrosyn:\nWe are a startup.")
    result = service.segment(doc)

    assert result.success
    assert result.document is not None
    assert result.duration_ms is not None
    assert len(result.document.sections) > 0


def test_segmentation_service_error():
    service = SegmentationService()

    # Pydantic validates input so we bypass validation to force error or pass invalid object
    # If raw_text is empty, but we somehow bypass validation:
    class FakeRawDocument:
        raw_text = None
        source_type = None
        source_url = None

    # Let's pass a bad object
    result = service.segment(FakeRawDocument())  # type: ignore
    assert not result.success
    assert result.error is not None


def test_segmentation_fixtures():
    service = SegmentationService()

    fixtures = ["naukri", "greenhouse", "lever", "indeed", "foundit", "workable"]

    for fix in fixtures:
        input_path = os.path.join(FIXTURE_DIR, f"{fix}.txt")
        expected_path = os.path.join(FIXTURE_DIR, f"{fix}_expected.json")

        assert os.path.exists(input_path), f"Input file {input_path} missing"
        assert os.path.exists(expected_path), f"Expected file {expected_path} missing"

        with open(input_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        with open(expected_path, "r", encoding="utf-8") as f:
            expected_output = json.load(f)

        raw_doc = RawDocument(
            raw_text=raw_text, source_type=fix, source_url=f"http://example.com/{fix}"
        )
        result = service.segment(raw_doc)

        assert result.success, f"Failed to segment {fix}: {result.error}"
        assert result.document is not None

        output = result.document.to_output()

        # Let's check that the output matches the expected JSON structure
        # (Compare keys and lines)
        for key in expected_output:
            assert key in output
            # Compare length/lines to make sure they are segmented as expected
            expected_lines = [
                line.strip() for line in expected_output[key] if line.strip()
            ]
            actual_lines = [line.strip() for line in output[key] if line.strip()]
            assert actual_lines == expected_lines, f"Mismatch in {fix} for key: {key}"
