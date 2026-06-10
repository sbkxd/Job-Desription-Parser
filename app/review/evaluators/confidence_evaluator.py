"""Confidence evaluation engine for determining when human review is required."""

from app.review.schemas.schemas import ReviewStatusSchema


class ConfidenceEvaluator:
    """Evaluates skill normalization confidence levels and flags uncertainties."""

    def __init__(
        self,
        auto_approve_threshold: float = 0.90,
        review_recommended_threshold: float = 0.75,
    ) -> None:
        self.auto_approve_threshold = auto_approve_threshold
        self.review_recommended_threshold = review_recommended_threshold

    def evaluate(
        self, confidence: float, match_method: str
    ) -> tuple[ReviewStatusSchema, str]:
        """Evaluate a confidence score and return the review status and reason.

        Args:
            confidence: The matching confidence score.
            match_method: The matching method used (e.g. 'exact', 'alias', 'fuzzy', 'embedding', 'none').

        Returns:
            A tuple of (ReviewStatusSchema, review_reason_string).
        """
        if match_method == "none" or confidence <= 0.0:
            return ReviewStatusSchema.PENDING, "OUT_OF_TAXONOMY"

        if confidence >= self.auto_approve_threshold:
            return ReviewStatusSchema.APPROVED, "AUTO_APPROVED"

        if confidence >= self.review_recommended_threshold:
            return ReviewStatusSchema.PENDING, "REVIEW_RECOMMENDED"

        return ReviewStatusSchema.PENDING, "REVIEW_REQUIRED"
