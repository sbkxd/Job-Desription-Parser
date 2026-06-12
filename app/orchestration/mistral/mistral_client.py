"""Official Mistral API client implementation for fallback resolution (Milestone 8.1)."""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, List, Optional, Type, TypeVar

from mistralai.client import Mistral
from pydantic import BaseModel

from app.orchestration.mistral.response_parser import ResponseParser
from app.orchestration.mistral.schemas import MistralInvocationAudit

logger = logging.getLogger(__name__)


T = TypeVar("T", bound=BaseModel)


class MistralClient:
    """Client wrapper for Mistral Small Latest API interactions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "mistral-small-latest",
        timeout_seconds: float = 15.0,
        max_retries: int = 3,
    ) -> None:
        from app.config.settings import settings

        self.api_key = (
            api_key or settings.MISTRAL_API_KEY or os.environ.get("MISTRAL_API_KEY", "")
        )
        self.model = model
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.audit_log: List[MistralInvocationAudit] = []

        if not self.api_key:
            logger.warning("MISTRAL_API_KEY is not set in environment variables.")

        # Mask API key for logs
        masked_key = "NOT_SET"
        if self.api_key:
            masked_key = (
                self.api_key[:4] + "..." + self.api_key[-4:]
                if len(self.api_key) > 8
                else "SET"
            )
        logger.info(
            "Initializing MistralClient with model=%s, api_key=%s",
            self.model,
            masked_key,
        )

        # Initialize the official SDK client
        self.client = Mistral(api_key=self.api_key)

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        prompt_version: str = "v1",
    ) -> T:
        """Call Mistral chat completion API and parse response into the given Pydantic schema.

        Args:
            prompt: User prompt content.
            schema: Pydantic model for response validation.
            system_prompt: Optional system instructions.
            prompt_version: Prompt template identifier for auditing.

        Returns:
            Validated Pydantic model instance.

        Raises:
            RuntimeError: If all retries fail.
        """
        messages: List[Any] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            request_ts = datetime.utcnow().isoformat()
            start_time = time.perf_counter()

            try:
                # Execute completion call
                logger.info(
                    "Calling Mistral API (attempt %d/%d)", attempt + 1, self.max_retries
                )

                # Wrap the async completion call
                response = await self.client.chat.complete_async(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    timeout_ms=int(self.timeout * 1000),
                )

                latency_ms = (time.perf_counter() - start_time) * 1000.0
                response_ts = datetime.utcnow().isoformat()

                raw_content = ""
                if response.choices and len(response.choices) > 0:
                    msg = response.choices[0].message
                    if msg and msg.content:
                        if isinstance(msg.content, str):
                            raw_content = msg.content
                        else:
                            raw_content = str(msg.content)

                # Parse and validate response
                validated_model = ResponseParser.parse_and_validate(raw_content, schema)
                assert isinstance(validated_model, schema)

                # Track token metrics
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0
                if response.usage:
                    prompt_tokens = response.usage.prompt_tokens or 0
                    completion_tokens = response.usage.completion_tokens or 0
                    total_tokens = response.usage.total_tokens or 0

                # Audit record
                audit = MistralInvocationAudit(
                    prompt_version=prompt_version,
                    model_version=self.model,
                    request_timestamp=request_ts,
                    response_timestamp=response_ts,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    latency_ms=latency_ms,
                    status="success",
                )
                self.audit_log.append(audit)

                logger.info(
                    "Mistral API call succeeded. Latency: %.2fms. Tokens: %d prompt / %d completion / %d total",
                    latency_ms,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                )

                return validated_model

            except Exception as e:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                response_ts = datetime.utcnow().isoformat()
                last_error = e

                logger.warning(
                    "Mistral call failed on attempt %d/%d: %s",
                    attempt + 1,
                    self.max_retries,
                    str(e),
                )

                audit = MistralInvocationAudit(
                    prompt_version=prompt_version,
                    model_version=self.model,
                    request_timestamp=request_ts,
                    response_timestamp=response_ts,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    latency_ms=latency_ms,
                    status="failed",
                    error_message=str(e),
                )
                self.audit_log.append(audit)

                # Wait before retry with backoff (except last attempt)
                if attempt < self.max_retries - 1:
                    sleep_time = 2.0 ** (attempt + 1)
                    logger.info("Retrying in %.2fs...", sleep_time)
                    await asyncio.sleep(sleep_time)

        # If we got here, all attempts failed
        raise RuntimeError(
            f"Mistral integration failed after {self.max_retries} attempts: {str(last_error)}"
        ) from last_error
