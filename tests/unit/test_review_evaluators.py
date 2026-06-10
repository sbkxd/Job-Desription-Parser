"""Unit tests for Phase 6 Review Evaluators (ConfidenceEvaluator and OutOfTaxonomyDetector)."""

from app.review.evaluators.confidence_evaluator import ConfidenceEvaluator
from app.review.evaluators.out_of_taxonomy import OutOfTaxonomyDetector
from app.review.schemas.schemas import ReviewStatusSchema


def test_confidence_evaluator_thresholds() -> None:
    evaluator = ConfidenceEvaluator(
        auto_approve_threshold=0.90, review_recommended_threshold=0.75
    )

    # 1. Auto Approve
    status, reason = evaluator.evaluate(0.95, "exact")
    assert status == ReviewStatusSchema.APPROVED
    assert reason == "AUTO_APPROVED"

    # 2. Review Recommended
    status, reason = evaluator.evaluate(0.85, "alias")
    assert status == ReviewStatusSchema.PENDING
    assert reason == "REVIEW_RECOMMENDED"

    # 3. Review Required
    status, reason = evaluator.evaluate(0.70, "embedding")
    assert status == ReviewStatusSchema.PENDING
    assert reason == "REVIEW_REQUIRED"

    # 4. Out of taxonomy / None match
    status, reason = evaluator.evaluate(0.0, "none")
    assert status == ReviewStatusSchema.PENDING
    assert reason == "OUT_OF_TAXONOMY"


def test_out_of_taxonomy_detector() -> None:
    detector = OutOfTaxonomyDetector()

    # 1. Known gap
    res = detector.detect("LangChain")
    assert res["review_required"] is True
    assert res["reason"] == "OUT_OF_TAXONOMY"
    assert res["normalized_skill"] is None

    # 2. In taxonomy
    res = detector.detect("Python", esco_id="esco_python")
    assert res["review_required"] is False
    assert res["reason"] == "IN_TAXONOMY"
    assert res["normalized_skill"] == "Python"

    # 3. Unmapped ESCO ID
    res = detector.detect("random_tech", esco_id="unmapped")
    assert res["review_required"] is True
    assert res["reason"] == "OUT_OF_TAXONOMY"
    assert res["normalized_skill"] is None
