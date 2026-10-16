"""Integration tests for API endpoints — /health and /chat/completions.

Uses FastAPI's TestClient with mocked LLM dependencies so that
no real provider calls are made.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

import app.main as main_module
from app.chat_service import ChatService
from app.config import Settings
from app.exceptions import (
    LLMAuthenticationError,
    LLMInvalidRequestError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.llm_client import OpenAIClient
from app.main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_completion(
    content: str = "Mock response",
    model: str = "gpt-4o-mini",
) -> ChatCompletion:
    return ChatCompletion(
        id="chatcmpl-api-test",
        created=1700000000,
        model=model,
        object="chat.completion",
        choices=[
            Choice(
                index=0,
                finish_reason="stop",
                message=ChatCompletionMessage(role="assistant", content=content),
            )
        ],
        usage=CompletionUsage(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        ),
    )


def _test_settings() -> Settings:
    return Settings(
        _env_file=None,  # type: ignore[call-arg]
        openai_api_key="sk-test",
        openai_model="gpt-4o-mini",
        openai_timeout_seconds=10.0,
        openai_max_retries=0,
    )


@pytest.fixture()
def mock_service():
    """Yield a mock ChatService injected into the app module."""
    mock_client = MagicMock(spec=OpenAIClient)
    service = ChatService(mock_client)

    original = main_module._chat_service
    main_module._chat_service = service
    yield service, mock_client
    main_module._chat_service = original


@pytest.fixture()
def client():
    """Create a TestClient that does NOT trigger lifespan (to avoid
    real OpenAI client instantiation)."""
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# /health — backward compatibility with M1
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """Ensure /health still works exactly as in Milestone 1."""

    def test_health_returns_ok(self, client) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /chat/completions — happy path
# ---------------------------------------------------------------------------


class TestChatCompletionEndpoint:
    """Test the chat completion endpoint with mocked LLM client."""

    def test_successful_completion(self, client, mock_service) -> None:
        service, mock_client = mock_service
        mock_client.create_chat_completion.return_value = _fake_completion(
            "Test answer"
        )

        response = client.post(
            "/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Test answer"
        assert body["model"] == "gpt-4o-mini"
        assert body["usage"]["total_tokens"] == 15

    def test_completion_with_overrides(self, client, mock_service) -> None:
        service, mock_client = mock_service
        mock_client.create_chat_completion.return_value = _fake_completion(
            "Custom", model="gpt-4o"
        )

        response = client.post(
            "/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 100,
            },
        )

        assert response.status_code == 200
        call_kwargs = mock_client.create_chat_completion.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["temperature"] == 0.1
        assert call_kwargs["max_tokens"] == 100

    def test_multi_message_conversation(self, client, mock_service) -> None:
        service, mock_client = mock_service
        mock_client.create_chat_completion.return_value = _fake_completion(
            "Follow-up answer"
        )

        response = client.post(
            "/chat/completions",
            json={
                "messages": [
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "What is Python?"},
                    {"role": "assistant", "content": "Python is a language."},
                    {"role": "user", "content": "Tell me more."},
                ],
            },
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Follow-up answer"


# ---------------------------------------------------------------------------
# POST /chat/completions — validation errors
# ---------------------------------------------------------------------------


class TestChatCompletionValidation:
    """Test request validation."""

    def test_empty_messages_rejected(self, client, mock_service) -> None:
        response = client.post(
            "/chat/completions",
            json={"messages": []},
        )
        assert response.status_code == 422

    def test_missing_messages_rejected(self, client, mock_service) -> None:
        response = client.post(
            "/chat/completions",
            json={},
        )
        assert response.status_code == 422

    def test_invalid_role_rejected(self, client, mock_service) -> None:
        response = client.post(
            "/chat/completions",
            json={"messages": [{"role": "hacker", "content": "hi"}]},
        )
        assert response.status_code == 422

    def test_empty_content_rejected(self, client, mock_service) -> None:
        response = client.post(
            "/chat/completions",
            json={"messages": [{"role": "user", "content": ""}]},
        )
        assert response.status_code == 422

    def test_temperature_too_high(self, client, mock_service) -> None:
        response = client.post(
            "/chat/completions",
            json={
                "messages": [{"role": "user", "content": "hi"}],
                "temperature": 5.0,
            },
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /chat/completions — error handling
# ---------------------------------------------------------------------------


class TestChatCompletionErrors:
    """Verify that LLM exceptions are translated to correct HTTP responses."""

    def test_auth_error_returns_401(self, client, mock_service) -> None:
        _, mock_client = mock_service
        mock_client.create_chat_completion.side_effect = LLMAuthenticationError(
            "Invalid API key"
        )

        response = client.post(
            "/chat/completions",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )

        assert response.status_code == 401
        assert "Invalid API key" in response.json()["error"]

    def test_rate_limit_returns_429(self, client, mock_service) -> None:
        _, mock_client = mock_service
        mock_client.create_chat_completion.side_effect = LLMRateLimitError(
            "Rate limit exceeded"
        )

        response = client.post(
            "/chat/completions",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )

        assert response.status_code == 429

    def test_timeout_returns_504(self, client, mock_service) -> None:
        _, mock_client = mock_service
        mock_client.create_chat_completion.side_effect = LLMTimeoutError(
            "Timed out"
        )

        response = client.post(
            "/chat/completions",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )

        assert response.status_code == 504

    def test_invalid_request_returns_422(self, client, mock_service) -> None:
        _, mock_client = mock_service
        mock_client.create_chat_completion.side_effect = LLMInvalidRequestError(
            "Bad model"
        )

        response = client.post(
            "/chat/completions",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )

        assert response.status_code == 422

    def test_provider_error_returns_502(self, client, mock_service) -> None:
        _, mock_client = mock_service
        mock_client.create_chat_completion.side_effect = LLMProviderError(
            "Server error"
        )

        response = client.post(
            "/chat/completions",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )

        assert response.status_code == 502
        assert "Server error" in response.json()["error"]
