"""Module for parsing and validating Mistral Small Latest responses."""

import json
import logging
from typing import Type

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parses and validates JSON responses from Mistral against Pydantic models."""

    @staticmethod
    def parse_and_validate(raw_response: str, schema: Type[BaseModel]) -> BaseModel:
        """Parses a raw string response, extracts JSON, and validates against the schema.

        Args:
            raw_response: Raw string from model completion.
            schema: Pydantic model class to validate against.

        Returns:
            An instance of the validated Pydantic model schema.

        Raises:
            ValueError: If parsing or validation fails.
        """
        cleaned = raw_response.strip()

        # Handle markdown blocks if present
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        # Try to locate JSON boundary if there's surrounding text
        if not (cleaned.startswith("{") or cleaned.startswith("[")):
            # Look for first '{' and last '}'
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                cleaned = cleaned[start_idx : end_idx + 1]

        try:
            parsed_json = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON from response: '%s'", raw_response)
            raise ValueError(f"Invalid JSON format: {str(e)}") from e

        try:
            validated = schema.model_validate(parsed_json)
            # Extra confidence checking if schema has confidence field
            if hasattr(validated, "confidence"):
                conf = getattr(validated, "confidence")  # noqa: B009
                if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
                    raise ValueError(
                        f"Confidence score {conf} is out of bounds [0.0, 1.0]"
                    )
            return validated
        except (ValidationError, ValueError) as e:
            logger.error(
                "Validation failed for schema %s: %s. Data: %s",
                schema.__name__,
                str(e),
                parsed_json,
            )
            raise ValueError(f"Schema validation failed: {str(e)}") from e
