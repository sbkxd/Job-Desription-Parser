"""Candidate ranking and confidence scoring engine for skill normalization."""

from app.normalization.schemas.schemas import NormalizedSkill, SkillCandidate


class CandidateRanker:
    """Aggregates candidates, ranks them based on method and score, and assigns final confidence."""

    # Method priority: Exact > Alias > Fuzzy > Embedding
    METHOD_PRIORITY = {
        "exact": 4,
        "alias": 3,
        "fuzzy": 2,
        "embedding": 1,
    }

    def rank(
        self, raw_skill: str, candidates: list[SkillCandidate]
    ) -> NormalizedSkill | None:
        """Select the best match from a list of candidates and generate the NormalizedSkill.

        Args:
            raw_skill: The raw extracted skill term.
            candidates: List of match candidates.

        Returns:
            NormalizedSkill if a valid candidate exists, else None.
        """
        if not candidates:
            return None

        # Sort candidates using a compound key:
        # 1. Method priority (higher is better)
        # 2. Score (higher is better)
        # 3. Canonical term length (shorter is often more general/correct, e.g. "React" over "React Router" if scores are equal)
        # 4. Canonical name alphabetically (deterministic tie-breaker)
        def sort_key(c: SkillCandidate) -> tuple[int, float, int, str]:
            priority = self.METHOD_PRIORITY.get(c.match_method, 0)
            term_len = -len(c.esco_skill.name)
            return (priority, c.score, term_len, c.esco_skill.name.lower())

        sorted_candidates = sorted(candidates, key=sort_key, reverse=True)
        best_candidate = sorted_candidates[0]

        # Calibrate confidence and assign match method details
        confidence = self.calibrate_confidence(best_candidate)

        return NormalizedSkill(
            raw_skill=raw_skill,
            normalized_skill=best_candidate.esco_skill.name,
            esco_id=best_candidate.esco_skill.esco_id,
            confidence=confidence,
            match_method=best_candidate.match_method,
        )

    @staticmethod
    def calibrate_confidence(candidate: SkillCandidate) -> float:
        """Calculate and calibrate the final confidence score based on the match method and raw score.

        Scoring Rules:
        - Exact match: 1.0
        - Alias match: 0.95
        - Fuzzy match: Maps raw similarity score (0.0 to 1.0) directly.
        - Embedding match: Maps cosine similarity (0.0 to 1.0) directly.

        Args:
            candidate: The selected winning SkillCandidate.

        Returns:
            Calibrated confidence float in range [0.0, 1.0].
        """
        if candidate.match_method == "exact":
            return 1.0
        if candidate.match_method == "alias":
            return 0.95

        # For fuzzy and embedding, return the score rounded to 2 decimal places
        return round(float(candidate.score), 2)
