"""Abstract base class and interface definitions for noise rules."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class NoiseRule(ABC):
    """Abstract base class representing a single content filtering rule."""

    @abstractmethod
    def evaluate(self, text: str) -> Dict[str, Any]:
        """Evaluate a text string to determine if it constitutes noise.

        Args:
            text: The text line or block to analyze.

        Returns:
            A dictionary containing:
              - is_noise (bool)
              - category (str)
              - confidence (float)
        """
        pass
