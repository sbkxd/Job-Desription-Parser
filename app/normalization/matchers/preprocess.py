"""Skill name preprocessing utility for canonical comparisons."""

import re


def clean_skill_name(name: str) -> str:
    """Preprocess raw skill names to make different surface forms comparable.

    Applies lowercasing, strips whitespaces, removes common web framework suffixes
    (e.g., .js, js, javascript), and cleans punctuation.

    Args:
        name: The raw skill name string.

    Returns:
        A cleaned, standardized string.
    """
    # 1. Lowercase and strip whitespace
    cleaned = name.lower().strip()

    # 2. Normalize common web framework suffixes (.js, js, javascript, etc.) at the end
    cleaned = re.sub(r"[\.\-\s]?js$", "", cleaned)
    cleaned = re.sub(r"[\.\-\s]?javascript$", "", cleaned)

    # 3. Remove spaces, dots, hyphens, and slashes to normalize styling variations
    cleaned = re.sub(r"[\.\-\s/]", "", cleaned)

    return cleaned
