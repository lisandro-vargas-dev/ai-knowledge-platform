"""Unit tests for app.llm_client — OpenAI client wrapper.

All tests use mocks — no real API calls are made.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import openai
import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from app.config import Settings
from app.exceptions import (
    LLMAuthenticationError,
    LLMInvalidRequestError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.llm_client import OpenAIClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_settings(**overrides) -> Settings:
    """Create a Settings instance with test defaults (no .env file)."""
    defaults = {
        "openai_api_key": "sk-test-key",
        "openai_model": "gpt-4o-mini",
        "openai_base_url": "https://api.openai.com/v1",
        "openai_timeout_seconds": 10.0,
        "openai_max_retries": 0,
        "openai_max_tokens": 256,
        "openai_temperature": 0.5,
    }
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)  # type: ignore[call-arg]


def _fake_completion(
    content: str = "Hello!",
    model: str = "gpt-4o-mini",
    prompt_tokens: int = 10,
    completion_tokens: int = 5,
) -> ChatCompletion:
    """Build a realistic ChatCompletion object for testing."""
    return ChatCompletion(
        id="chatcmpl-test-123",
        created=1700000000,
        model=model,
        object="chat.completion",
        choices=[
            Choice(
                index=0,
                finish_reason="stop",
                message=ChatCompletionMessage(
                    role="assistant",
                    content=content,
                ),
            )
        ],
        usage=CompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestOpenAIClientSuccess:
    """Verify the happy-path behaviour with a mocked SDK."""

    def test_returns_chat_completion(self) -> None:
        settings = _make_settings()
        client = OpenAIClient(settings)

        fake = _fake_completion("Hi there", model="gpt-4o-mini")

        with patch.object(
            client._client.chat.completions, "create", return_value=fake
        ) as mock_create:
            result = client.create_chat_completion(
                messages=[{"role": "user", "content": "Hello"}]
            )

        mock_create.assert_called_once()
        assert result.choices[0].message.content == "Hi there"
        assert result.model == "gpt-4o-mini"
        assert result.usage is not None
        assert result.usage.total_tokens == 15

    def test_uses_configured_defaults(self) -> None:
        settings = _make_settings(
            openai_model="gpt-4o",
            openai_temperature=0.2,
            openai_max_tokens=512,
        )
        client = OpenAIClient(settings)

        fake = _fake_completion(model="gpt-4o")
        with patch.object(
            client._client.chat.completions, "create", return_value=fake
        ) as mock_create:
            client.create_chat_completion(
                messages=[{"role": "user", "content": "test"}]
            )

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["temperature"] == 0.2
        assert call_kwargs["max_tokens"] == 512

    def test_overrides_take_precedence(self) -> None:
        settings = _make_settings()
        client = OpenAIClient(settings)

        fake = _fake_completion(model="gpt-4o")
        with patch.object(
            client._client.chat.completions, "create", return_value=fake
        ) as mock_create:
            client.create_chat_completion(
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
                temperature=0.0,
                max_tokens=100,
            )

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["temperature"] == 0.0
        assert call_kwargs["max_tokens"] == 100


class TestOpenAIClientErrors:
    """Verify that SDK exceptions are mapped to application exceptions."""

    def _make_client(self) -> OpenAIClient:
        return OpenAIClient(_make_settings())

    def _messages(self) -> list[dict[str, str]]:
        return [{"role": "user", "content": "Hi"}]

    def test_authentication_error(self) -> None:
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.headers = {}
        mock_response.json.return_value = {"error": {"message": "bad key"}}

        with patch.object(
            client._client.chat.completions,
            "create",
            side_effect=openai.AuthenticationError(
                message="bad key",
                response=mock_response,
                body={"error": {"message": "bad key"}},
            ),
        ):
            with pytest.raises(LLMAuthenticationError, match="Invalid or missing API key"):
                client.create_chat_completion(self._messages())

    def test_rate_limit_error(self) -> None:
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}
        mock_response.json.return_value = {
            "error": {"message": "rate limited"}
        }

        with patch.object(
            client._client.chat.completions,
            "create",
            side_effect=openai.RateLimitError(
                message="rate limited",
                response=mock_response,
                body={"error": {"message": "rate limited"}},
            ),
        ):
            with pytest.raises(LLMRateLimitError, match="Rate limit exceeded"):
                client.create_chat_completion(self._messages())

    def test_timeout_error(self) -> None:
        client = self._make_client()
        mock_request = MagicMock()

        with patch.object(
            client._client.chat.completions,
            "create",
            side_effect=openai.APITimeoutError(request=mock_request),
        ):
            with pytest.raises(LLMTimeoutError, match="timed out"):
                client.create_chat_completion(self._messages())

    def test_bad_request_error(self) -> None:
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.headers = {}
        mock_response.json.return_value = {
            "error": {"message": "invalid model"}
        }

        with patch.object(
            client._client.chat.completions,
            "create",
            side_effect=openai.BadRequestError(
                message="invalid model",
                response=mock_response,
                body={"error": {"message": "invalid model"}},
            ),
        ):
            with pytest.raises(LLMInvalidRequestError, match="rejected"):
                client.create_chat_completion(self._messages())

    def test_server_error(self) -> None:
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_response.json.return_value = {
            "error": {"message": "internal"}
        }

        with patch.object(
            client._client.chat.completions,
            "create",
            side_effect=openai.InternalServerError(
                message="internal",
                response=mock_response,
                body={"error": {"message": "internal"}},
            ),
        ):
            with pytest.raises(LLMProviderError, match="status 500"):
                client.create_chat_completion(self._messages())

    def test_connection_error(self) -> None:
        client = self._make_client()
        mock_request = MagicMock()

        with patch.object(
            client._client.chat.completions,
            "create",
            side_effect=openai.APIConnectionError(request=mock_request),
        ):
            with pytest.raises(LLMProviderError, match="Could not connect"):
                client.create_chat_completion(self._messages())
