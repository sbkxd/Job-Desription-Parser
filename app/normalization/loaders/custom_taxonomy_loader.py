"""Loader for custom taxonomy extensions to augment the canonical ESCO taxonomy."""

import glob
import json
import os

from app.normalization.schemas.schemas import EscoSkill

_DEFAULT_CUSTOM_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "data",
    "custom_taxonomy",
)


class CustomTaxonomyLoader:
    """Loads custom taxonomy extensions from data/custom_taxonomy/."""

    def __init__(self, custom_dir: str = _DEFAULT_CUSTOM_DIR) -> None:
        self.custom_dir = custom_dir

    def load(self) -> list[EscoSkill]:
        """Loads and converts custom skills to EscoSkill instances.

        Returns:
            List of EscoSkill objects.
        """
        if not os.path.exists(self.custom_dir):
            return []

        custom_skills: list[EscoSkill] = []
        # Find all JSON files in the custom taxonomy directory
        json_pattern = os.path.join(self.custom_dir, "*.json")
        for file_path in glob.glob(json_pattern):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)

                items = content if isinstance(content, list) else [content]
                for item in items:
                    skill_name = item.get("skill")
                    if not skill_name:
                        continue

                    category = item.get("category", "Custom Skill")
                    aliases = item.get("aliases", [])

                    # Construct unique local esco_id starting with 'custom_'
                    esco_id = f"custom_{skill_name.lower().strip().replace(' ', '_')}"
                    custom_skills.append(
                        EscoSkill(
                            esco_id=esco_id,
                            name=skill_name,
                            description=category,
                            alternative_labels=aliases,
                        )
                    )
            except Exception:
                # Log or ignore corrupted files
                continue

        return custom_skills
