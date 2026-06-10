"""Taxonomy repository for loading, indexing, and lookup of ESCO skills."""

from typing import Any

import numpy as np

# sentence-transformers is imported dynamically to enable clean lazy loading
# and CPU/GPU device selection config.
from sentence_transformers import SentenceTransformer

from app.normalization.loaders.custom_taxonomy_loader import CustomTaxonomyLoader
from app.normalization.loaders.taxonomy_loader import TaxonomyLoader
from app.normalization.schemas.schemas import EscoSkill


class TaxonomyRepository:
    """Singleton-like repository that indexes ESCO skills for fast multi-match search."""

    _instance: "TaxonomyRepository | None" = None
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any) -> "TaxonomyRepository":
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        loader: TaxonomyLoader | None = None,
        custom_loader: CustomTaxonomyLoader | None = None,
    ) -> None:
        if self._initialized:
            return

        self.loader = loader or TaxonomyLoader()
        self.custom_loader = custom_loader or CustomTaxonomyLoader()
        self.skills: list[EscoSkill] = []

        # In-memory indexes
        self.exact_index: dict[str, EscoSkill] = {}
        self.alias_index: dict[str, EscoSkill] = {}

        # Embeddings caching structures
        self.model: SentenceTransformer | None = None
        self.embeddings_matrix: np.ndarray | None = None
        self.skills_by_index: list[EscoSkill] = []

        self.initialize()
        self._initialized = True

    def initialize(self) -> None:
        """Load taxonomy data and build search indexes."""
        # 1. Load taxonomy dataset
        self.skills = self.loader.load()

        # Load custom taxonomy extensions
        custom_skills = self.custom_loader.load()
        self.skills.extend(custom_skills)

        # 2. Build Exact and Alias indexes
        for skill in self.skills:
            # Canonical name exact match index
            self.exact_index[skill.name.lower().strip()] = skill

            # Alternative labels/aliases index
            for alias in skill.alternative_labels:
                self.alias_index[alias.lower().strip()] = skill

        # 3. Load Sentence-Transformer model for embeddings
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # 4. Precompute embeddings for all canonical skills
        if self.skills:
            skill_names = [skill.name for skill in self.skills]
            # model.encode returns a numpy ndarray of shape (num_skills, embedding_dim)
            self.embeddings_matrix = self.model.encode(
                skill_names, show_progress_bar=False, convert_to_numpy=True
            )
            self.skills_by_index = list(self.skills)

    def find_exact(self, name: str) -> EscoSkill | None:
        """Find a skill by exact canonical name match (case-insensitive)."""
        return self.exact_index.get(name.lower().strip())

    def find_alias(self, name: str) -> EscoSkill | None:
        """Find a skill by exact alternative label / alias match (case-insensitive)."""
        return self.alias_index.get(name.lower().strip())

    def get_all_skills(self) -> list[EscoSkill]:
        """Return all skills loaded in the repository."""
        return self.skills

    def get_model(self) -> SentenceTransformer:
        """Return the sentence-transformer model instance."""
        if self.model is None:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        return self.model

    def get_embeddings_matrix(self) -> tuple[np.ndarray | None, list[EscoSkill]]:
        """Return the precomputed embeddings matrix and the corresponding skills list."""
        return self.embeddings_matrix, self.skills_by_index
