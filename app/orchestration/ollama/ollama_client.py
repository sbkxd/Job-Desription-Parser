"""API client for invoking local Ollama model instances."""

import json
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama service running qwen3:4b."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:4b",
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout_seconds
        self.max_retries = max_retries

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Call Ollama's generate endpoint.

        Args:
            prompt: The text prompt.
            system: Optional system prompt context.

        Returns:
            The raw string response from the model.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0},
        }
        if system:
            payload["system"] = system

        for attempt in range(self._get_retries_count()):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    return str(data.get("response", "")).strip()
            except Exception as e:
                logger.warning(
                    "Ollama call failed on attempt %d/%d: %s",
                    attempt + 1,
                    self._get_retries_count(),
                    str(e),
                )
                if attempt == self._get_retries_count() - 1:
                    raise RuntimeError(
                        f"Ollama integration failed after {self._get_retries_count()} attempts: {str(e)}"
                    ) from e

        return ""

    def _get_retries_count(self) -> int:
        return max(1, self.max_retries)

    async def generate_json(
        self, prompt: str, system: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call Ollama's generate endpoint and parse the response as JSON.

        Args:
            prompt: The text prompt.
            system: Optional system prompt.

        Returns:
            A parsed JSON dictionary.
        """
        raw_response = await self.generate(prompt, system=system)
        try:
            # Strip markdown code blocks if any got through despite prompt instructions
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()

            return dict(json.loads(cleaned))
        except Exception as e:
            logger.error(
                "Failed to parse JSON from Ollama response: '%s', error: %s",
                raw_response,
                str(e),
            )
            # Return empty structure or mock fallback
            return {}
