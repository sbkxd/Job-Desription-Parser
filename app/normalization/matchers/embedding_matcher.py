"""Embedding-based semantic similarity match engine for skill normalization."""

import numpy as np

from app.normalization.schemas.schemas import SkillCandidate
from app.normalization.taxonomy.taxonomy_repository import TaxonomyRepository

DEFAULT_EMBEDDING_THRESHOLD = 0.5


class EmbeddingMatcher:
    """Uses sentence-transformers embeddings and cosine similarity to map skills."""

    def __init__(
        self,
        repository: TaxonomyRepository,
        threshold: float = DEFAULT_EMBEDDING_THRESHOLD,
    ) -> None:
        self.repository = repository
        self.threshold = threshold

    def match_candidates(self, raw_name: str, top_k: int = 3) -> list[SkillCandidate]:
        """Perform semantic embedding search against the taxonomy.

        Args:
            raw_name: The extracted raw skill name.
            top_k: Number of top candidates to retrieve.

        Returns:
            List of SkillCandidate matches sorted by similarity score descending.
        """
        matrix, skills_by_index = self.repository.get_embeddings_matrix()
        if matrix is None or len(skills_by_index) == 0:
            return []

        # 1. Encode the input raw name
        model = self.repository.get_model()
        input_emb = model.encode(
            raw_name, show_progress_bar=False, convert_to_numpy=True
        )

        # 2. Calculate Cosine Similarity with the taxonomy embeddings matrix
        norm_input = float(np.linalg.norm(input_emb))
        norm_matrix = np.linalg.norm(matrix, axis=1)

        # Avoid division by zero
        norm_matrix[norm_matrix == 0] = 1.0
        if norm_input == 0.0:
            norm_input = 1.0

        similarities = np.dot(matrix, input_emb) / (norm_matrix * norm_input)

        # 3. Filter and rank results
        candidates: list[SkillCandidate] = []
        for idx, similarity in enumerate(similarities):
            score = float(similarity)
            if score >= self.threshold:
                candidates.append(
                    SkillCandidate(
                        esco_skill=skills_by_index[idx],
                        score=round(score, 2),
                        match_method="embedding",
                    )
                )

        # Sort by score descending and return top-k
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:top_k]

    def match(self, raw_name: str) -> SkillCandidate | None:
        """Find the single best semantic embedding match.

        Args:
            raw_name: The extracted raw skill name.

        Returns:
            The best SkillCandidate if found, else None.
        """
        results = self.match_candidates(raw_name, top_k=1)
        return results[0] if results else None
