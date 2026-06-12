"""Unit tests for the local Ollama client and adapter (Milestone 7.9)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.orchestration.ollama.ollama_client import OllamaClient
from app.orchestration.ollama.qwen_adapter import QwenAdapter


@pytest.mark.asyncio
async def test_ollama_client_generate() -> None:
    client = OllamaClient(max_retries=2)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "  Qwen output text  "}

    # Mock the httpx client post call
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await client.generate("Hello Qwen")
        assert res == "Qwen output text"
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_ollama_client_retry_logic() -> None:
    client = OllamaClient(max_retries=3)

    # First two attempts fail, third attempt succeeds
    mock_post = AsyncMock()
    mock_post.side_effect = [
        RuntimeError("Connection timeout"),
        RuntimeError("Internal Server Error"),
        MagicMock(status_code=200, json=lambda: {"response": "Success"}),
    ]

    with patch("httpx.AsyncClient.post", mock_post):
        res = await client.generate("Hello")
        assert res == "Success"
        assert mock_post.call_count == 3


@pytest.mark.asyncio
async def test_qwen_adapter_ambiguous_skill() -> None:
    mock_client = AsyncMock()
    mock_client.generate_json.return_value = {
        "selected_skill": "Apache Spark",
        "reason": "matches context",
    }
    adapter = QwenAdapter(client=mock_client)

    res = await adapter.resolve_ambiguous_skill(
        skill="Spark",
        context="big data analytics",
        candidates=["Apache Spark", "Spark Framework"],
    )
    assert res["selected_skill"] == "Apache Spark"
    assert res["reason"] == "matches context"
    mock_client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_qwen_adapter_assist_review() -> None:
    mock_client = AsyncMock()
    mock_client.generate_json.return_value = {
        "category": "AI Framework",
        "confidence": 0.85,
    }
    adapter = QwenAdapter(client=mock_client)

    res = await adapter.assist_review(
        skill="LangChain",
        context="LLM orchestrator",
        review_reason="OUT_OF_TAXONOMY",
    )
    assert res["category"] == "AI Framework"
    assert res["confidence"] == 0.85
