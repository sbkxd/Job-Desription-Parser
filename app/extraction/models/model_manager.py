"""Model Manager singleton for lazy loading and caching DeBERTa models."""

from typing import Any

from app.extraction.models.deberta_loader import DebertaLoader
from app.logging.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Singleton manager for the NER model pipeline."""

    _instance = None
    _pipeline = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "ModelManager":
        if not cls._instance:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Initialize loader configuration
        self.loader = DebertaLoader()

    def get_pipeline(self) -> Any:
        """Lazy load and return the DeBERTa NER pipeline.

        Falls back gracefully with logging if the pipeline cannot be initialized.
        """
        if self._pipeline is None:
            logger.info("Initializing DeBERTa model pipeline (lazy loading)...")
            try:
                self._pipeline = self.loader.load_pipeline()
                logger.info("DeBERTa model pipeline initialized successfully.")
            except Exception as e:
                logger.warning(
                    "Failed to load DeBERTa model. Falling back to rule-based mock pipeline.",
                    error=str(e),
                )
                self._pipeline = self._create_fallback_pipeline()
        return self._pipeline

    def _create_fallback_pipeline(self) -> Any:
        """Create a mock pipeline that acts like Hugging Face's pipeline but returns empty list."""

        def mock_pipeline(*args: Any, **kwargs: Any) -> list[Any]:
            return []

        return mock_pipeline
