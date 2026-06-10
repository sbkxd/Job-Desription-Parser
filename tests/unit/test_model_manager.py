from unittest.mock import patch

from app.extraction.models.model_manager import ModelManager


def test_model_manager_singleton():
    manager1 = ModelManager()
    manager2 = ModelManager()
    assert manager1 is manager2


def test_model_manager_lazy_loading_fallback():
    # Force failure to test fallback
    with patch(
        "app.extraction.models.deberta_loader.DebertaLoader.load_pipeline",
        side_effect=Exception("Failed to load"),
    ):
        manager = ModelManager()
        # Reset cached pipeline to force reload
        ModelManager._pipeline = None

        pipeline = manager.get_pipeline()
        assert pipeline is not None
        # Verify it behaves like fallback pipeline
        res = pipeline("any text")
        assert res == []
