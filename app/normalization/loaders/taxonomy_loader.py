"""Loader for the local ESCO skills taxonomy dataset."""

import json
import os

from app.normalization.schemas.schemas import EscoSkill

# Default path to the local ESCO JSON file
_DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "taxonomy",
    "esco_skills.json",
)


class TaxonomyLoader:
    """Loader to parse and return local ESCO taxonomy skills."""

    def __init__(self, dataset_path: str = _DEFAULT_DATASET_PATH) -> None:
        self.dataset_path = dataset_path

    def load(self) -> list[EscoSkill]:
        """Load and parse the local JSON file containing ESCO skills.

        Returns:
            List of EscoSkill objects.
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(
                f"ESCO taxonomy dataset not found at {self.dataset_path}"
            )

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [EscoSkill(**item) for item in data]
