"""Loader logic for DeBERTa models."""

from typing import Any

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# Default model path/name
DEFAULT_MODEL_NAME = "microsoft/deberta-v3-small"


class DebertaLoader:
    """Configures and loads the DeBERTa model and tokenizer for token classification."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1

    def load_pipeline(self) -> Any:
        """Load and return the token classification pipeline.

        Falls back to CPU if GPU is not available.
        """
        # Caching directory is handled by transformers default (or HF_HOME env var)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        # Using a default classification head (randomly initialized if base model)
        model = AutoModelForTokenClassification.from_pretrained(self.model_name)

        return pipeline(  # type: ignore[call-overload]
            "ner",
            model=model,
            tokenizer=tokenizer,
            device=self.device,
            aggregation_strategy="simple",
        )
