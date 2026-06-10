"""Alias match engine for skill normalization."""

from app.normalization.matchers.preprocess import clean_skill_name
from app.normalization.schemas.schemas import SkillCandidate
from app.normalization.taxonomy.taxonomy_repository import TaxonomyRepository


class AliasMatcher:
    """Matches raw skills against alternative labels (aliases) of canonical skills."""

    def __init__(self, repository: TaxonomyRepository) -> None:
        self.repository = repository

    def match(self, raw_name: str) -> SkillCandidate | None:
        """Attempt to find a match against the alias/alternative label index.

        Args:
            raw_name: The extracted raw skill name.

        Returns:
            A SkillCandidate if matched, else None.
        """
        # Try lookup with cleaned name
        cleaned_name = clean_skill_name(raw_name)
        matched_skill = self.repository.find_alias(cleaned_name)

        # Fallback to direct check in case cleaning was too aggressive
        if not matched_skill:
            matched_skill = self.repository.find_alias(raw_name.lower().strip())

        if matched_skill:
            return SkillCandidate(
                esco_skill=matched_skill,
                score=0.95,
                match_method="alias",
            )

        return None
