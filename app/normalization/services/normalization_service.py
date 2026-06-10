"""Skill normalization service orchestrating the matching pipeline."""

import time

from app.logging.logger import get_logger
from app.normalization.matchers.alias_matcher import AliasMatcher
from app.normalization.matchers.embedding_matcher import EmbeddingMatcher
from app.normalization.matchers.exact_matcher import ExactMatcher
from app.normalization.matchers.fuzzy_matcher import FuzzyMatcher
from app.normalization.rankers.candidate_ranker import CandidateRanker
from app.normalization.schemas.schemas import (
    NormalizationResult,
    NormalizedSkill,
    SkillCandidate,
)
from app.normalization.taxonomy.taxonomy_repository import TaxonomyRepository

logger = get_logger(__name__)


class SkillNormalizationService:
    """Orchestrates the preprocessing, matching, ranking, and scoring pipeline."""

    def __init__(self, repository: TaxonomyRepository | None = None) -> None:
        self.repository = repository or TaxonomyRepository()
        self.exact_matcher = ExactMatcher(self.repository)
        self.alias_matcher = AliasMatcher(self.repository)
        self.fuzzy_matcher = FuzzyMatcher(self.repository)
        self.embedding_matcher = EmbeddingMatcher(self.repository)
        self.ranker = CandidateRanker()

    def normalize(self, raw_skills: list[str]) -> NormalizationResult:
        """Normalize a list of raw skill strings into canonical ESCO skills.

        Args:
            raw_skills: List of extracted raw skill names.

        Returns:
            NormalizationResult containing a list of mapped/unmapped NormalizedSkill objects.
        """
        start_time = time.perf_counter()
        logger.info("Starting skill normalization pipeline", count=len(raw_skills))

        normalized_list: list[NormalizedSkill] = []

        # Deduplicate raw skills to optimize batch execution (Normalize once per unique skill)
        unique_raw_skills = list(dict.fromkeys(raw_skills))

        for raw_name in unique_raw_skills:
            if not raw_name or not raw_name.strip():
                continue

            candidates: list[SkillCandidate] = []

            # 1. Attempt Exact Match (high precision)
            exact_cand = self.exact_matcher.match(raw_name)
            if exact_cand:
                candidates.append(exact_cand)

            # 2. Attempt Alias Match
            alias_cand = self.alias_matcher.match(raw_name)
            if alias_cand:
                candidates.append(alias_cand)

            # 3. Attempt Fuzzy Match (RapidFuzz)
            fuzzy_cands = self.fuzzy_matcher.match_candidates(raw_name, top_k=3)
            candidates.extend(fuzzy_cands)

            # 4. Attempt Embedding Match (Semantic Search)
            embedding_cands = self.embedding_matcher.match_candidates(raw_name, top_k=3)
            candidates.extend(embedding_cands)

            # 5. Rank Candidates & Score
            best_match = self.ranker.rank(raw_name, candidates)

            if best_match:
                normalized_list.append(best_match)
            else:
                # Handle ESCO coverage gaps: Keep raw skill unmatched
                normalized_list.append(
                    NormalizedSkill(
                        raw_skill=raw_name,
                        normalized_skill=raw_name,
                        esco_id="unmapped",
                        confidence=0.0,
                        match_method="none",
                    )
                )

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "Skill normalization pipeline completed successfully",
            duration_ms=duration_ms,
            normalized_count=len(normalized_list),
        )

        return NormalizationResult(normalized_skills=normalized_list)
