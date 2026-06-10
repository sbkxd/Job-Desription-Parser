"""Exact match engine for skill normalization."""

from app.normalization.schemas.schemas import SkillCandidate
from app.normalization.taxonomy.taxonomy_repository import TaxonomyRepository


class ExactMatcher:
    """Matches raw skills against canonical taxonomy names exactly (case-insensitive)."""

    def __init__(self, repository: TaxonomyRepository) -> None:
        self.repository = repository

    def match(self, raw_name: str) -> SkillCandidate | None:
        """Attempt to find an exact case-insensitive match for the raw skill name.

        Args:
            raw_name: The extracted raw skill name.

        Returns:
            A SkillCandidate if matched, else None.
        """
        # Exact case-insensitive match against canonical name
        matched_skill = self.repository.find_exact(raw_name.lower().strip())

        if matched_skill:
            return SkillCandidate(
                esco_skill=matched_skill,
                score=1.0,
                match_method="exact",
            )

        return None
