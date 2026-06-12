"""Unit tests for the Mistral client, prompt builder, and parser (Milestone 8.3)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.orchestration.mistral.mistral_client import MistralClient
from app.orchestration.mistral.prompt_builder import PromptBuilder
from app.orchestration.mistral.response_parser import ResponseParser
from app.orchestration.mistral.schemas import (
    AmbiguousSkillSchema,
    ReviewAssistanceSchema,
)


@pytest.fixture
def mock_mistral_response():
    """Fixture to create a mock response matching Mistral SDK structure."""
    mock_choice = MagicMock()
    mock_choice.message.content = (
        '{"selected_skill": "Apache Spark", "reason": "matches context"}'
    )

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 15
    mock_usage.total_tokens = 25

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    mock_resp.usage = mock_usage
    return mock_resp


@pytest.mark.asyncio
async def test_mistral_client_generate_structured_success(
    mock_mistral_response,
) -> None:
    client = MistralClient(api_key="test_key", max_retries=1)

    # Patch complete_async on the underlying client instance
    with patch.object(
        client.client.chat, "complete_async", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = mock_mistral_response

        res = await client.generate_structured(
            prompt="Resolve Spark",
            schema=AmbiguousSkillSchema,
            system_prompt="System instructions",
        )

        assert isinstance(res, AmbiguousSkillSchema)
        assert res.selected_skill == "Apache Spark"
        assert res.reason == "matches context"
        assert len(client.audit_log) == 1
        assert client.audit_log[0].status == "success"
        assert client.audit_log[0].total_tokens == 25
        mock_complete.assert_called_once()


@pytest.mark.asyncio
async def test_mistral_client_retry_logic(mock_mistral_response) -> None:
    client = MistralClient(api_key="test_key", max_retries=3)

    # Mock asyncio.sleep to keep test fast
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with patch.object(
            client.client.chat, "complete_async", new_callable=AsyncMock
        ) as mock_complete:
            # First two calls raise exception, third succeeds
            mock_complete.side_effect = [
                RuntimeError("Rate limit exceeded"),
                RuntimeError("Gateway timeout"),
                mock_mistral_response,
            ]

            res = await client.generate_structured(
                prompt="Resolve", schema=AmbiguousSkillSchema
            )

            assert res.selected_skill == "Apache Spark"
            assert mock_complete.call_count == 3
            assert mock_sleep.call_count == 2
            assert len(client.audit_log) == 3
            assert client.audit_log[0].status == "failed"
            assert client.audit_log[2].status == "success"


@pytest.mark.asyncio
async def test_mistral_client_exhausts_retries() -> None:
    client = MistralClient(api_key="test_key", max_retries=3)

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with patch.object(
            client.client.chat, "complete_async", new_callable=AsyncMock
        ) as mock_complete:
            mock_complete.side_effect = RuntimeError("Fatal API Error")

            with pytest.raises(RuntimeError) as exc_info:
                await client.generate_structured(
                    prompt="Resolve", schema=AmbiguousSkillSchema
                )
            assert "Mistral integration failed" in str(exc_info.value)
            assert mock_complete.call_count == 3


def test_response_parser_extraction_json() -> None:
    # 1. Standard valid JSON
    raw_ok = '{"selected_skill": "Python", "reason": "matches developer role"}'
    res_ok = ResponseParser.parse_and_validate(raw_ok, AmbiguousSkillSchema)
    assert res_ok.selected_skill == "Python"

    # 2. Markdown wrapped JSON
    raw_md = '```json\n{"selected_skill": "SQL", "reason": "database skill"}\n```'
    res_md = ResponseParser.parse_and_validate(raw_md, AmbiguousSkillSchema)
    assert res_md.selected_skill == "SQL"

    # 3. Surrounding conversational text
    raw_convo = 'Here is the result:\n{"selected_skill": "Docker", "reason": "containerization"}\nHope this helps!'
    res_convo = ResponseParser.parse_and_validate(raw_convo, AmbiguousSkillSchema)
    assert res_convo.selected_skill == "Docker"

    # 4. Out-of-bounds confidence validation
    raw_bad_conf = '{"category": "Cloud", "confidence": 1.5}'
    with pytest.raises(ValueError) as exc:
        ResponseParser.parse_and_validate(raw_bad_conf, ReviewAssistanceSchema)
    assert "Confidence score 1.5 is out of bounds" in str(exc.value)


def test_prompt_builder() -> None:
    builder = PromptBuilder()

    prompt = builder.build_review_assistance_prompt(
        skill="FastAPI",
        context="web application development in python using FastAPI",
        review_reason="OUT_OF_TAXONOMY",
    )
    assert "FastAPI" in prompt
    assert "OUT_OF_TAXONOMY" in prompt
    assert "Strictly output ONLY valid JSON" in prompt
