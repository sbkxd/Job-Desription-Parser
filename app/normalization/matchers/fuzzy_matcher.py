"""Fuzzy match engine using RapidFuzz for skill normalization."""

from rapidfuzz import fuzz

from app.normalization.matchers.preprocess import clean_skill_name
from app.normalization.schemas.schemas import SkillCandidate
from app.normalization.taxonomy.taxonomy_repository import TaxonomyRepository

DEFAULT_FUZZY_THRESHOLD = 85.0


class FuzzyMatcher:
    """Fuzzy matcher to handle spelling variations and typos using RapidFuzz."""

    def __init__(
        self, repository: TaxonomyRepository, threshold: float = DEFAULT_FUZZY_THRESHOLD
    ) -> None:
        self.repository = repository
        self.threshold = threshold

    def match_candidates(self, raw_name: str, top_k: int = 3) -> list[SkillCandidate]:
        """Perform fuzzy matching against canonical names and aliases.

        Args:
            raw_name: The extracted raw skill name.
            top_k: Number of top candidates to retrieve.

        Returns:
            List of SkillCandidate matches sorted by score descending.
        """
        candidates: list[SkillCandidate] = []
        cleaned_raw = clean_skill_name(raw_name)

        for skill in self.repository.get_all_skills():
            best_score = 0.0

            # Match against canonical name
            cleaned_canon = clean_skill_name(skill.name)
            score_canon = fuzz.ratio(cleaned_raw, cleaned_canon)
            best_score = max(best_score, score_canon)

            # Match against aliases
            for alias in skill.alternative_labels:
                cleaned_alias = clean_skill_name(alias)
                score_alias = fuzz.ratio(cleaned_raw, cleaned_alias)
                best_score = max(best_score, score_alias)

            # Keep candidate if it exceeds the similarity threshold
            if best_score >= self.threshold:
                # Normalize score to [0.0, 1.0] range
                normalized_score = round(best_score / 100.0, 2)
                candidates.append(
                    SkillCandidate(
                        esco_skill=skill,
                        score=normalized_score,
                        match_method="fuzzy",
                    )
                )

        # Sort by score descending and return top-k
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:top_k]

    def match(self, raw_name: str) -> SkillCandidate | None:
        """Find the single best fuzzy match candidate.

        Args:
            raw_name: The extracted raw skill name.

        Returns:
            The best SkillCandidate if found, else None.
        """
        results = self.match_candidates(raw_name, top_k=1)
        return results[0] if results else None
