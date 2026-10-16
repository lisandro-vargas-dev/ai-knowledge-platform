"""Unit tests for app.chat_service — service layer logic.

All tests use mocks — no real API calls are made.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from app.chat_service import ChatService
from app.schemas import ChatCompletionRequest, ChatMessage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_completion(
    content: str = "I can help!",
    model: str = "gpt-4o-mini",
    prompt_tokens: int = 12,
    completion_tokens: int = 8,
) -> ChatCompletion:
    return ChatCompletion(
        id="chatcmpl-svc-test",
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


def _fake_completion_no_usage(content: str = "Hi") -> ChatCompletion:
    return ChatCompletion(
        id="chatcmpl-svc-test-no-usage",
        created=1700000000,
        model="gpt-4o-mini",
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
        usage=None,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestChatService:
    """Verify the service layer correctly bridges request ↔ client ↔ response."""

    def test_complete_returns_response(self) -> None:
        mock_client = MagicMock()
        mock_client.create_chat_completion.return_value = _fake_completion(
            content="Sure, I'll help.", model="gpt-4o-mini"
        )

        service = ChatService(mock_client)
        request = ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Help me")]
        )

        response = service.complete(request)

        assert response.message == "Sure, I'll help."
        assert response.model == "gpt-4o-mini"
        assert response.usage is not None
        assert response.usage.prompt_tokens == 12
        assert response.usage.completion_tokens == 8
        assert response.usage.total_tokens == 20

    def test_complete_without_usage(self) -> None:
        mock_client = MagicMock()
        mock_client.create_chat_completion.return_value = (
            _fake_completion_no_usage("Short answer")
        )

        service = ChatService(mock_client)
        request = ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Short")]
        )

        response = service.complete(request)

        assert response.message == "Short answer"
        assert response.usage is None

    def test_complete_forwards_overrides(self) -> None:
        mock_client = MagicMock()
        mock_client.create_chat_completion.return_value = _fake_completion(
            model="gpt-4o"
        )

        service = ChatService(mock_client)
        request = ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Test")],
            model="gpt-4o",
            temperature=0.1,
            max_tokens=64,
        )

        service.complete(request)

        call_kwargs = mock_client.create_chat_completion.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["temperature"] == 0.1
        assert call_kwargs["max_tokens"] == 64

    def test_complete_passes_messages_as_dicts(self) -> None:
        mock_client = MagicMock()
        mock_client.create_chat_completion.return_value = _fake_completion()

        service = ChatService(mock_client)
        request = ChatCompletionRequest(
            messages=[
                ChatMessage(role="system", content="You are helpful."),
                ChatMessage(role="user", content="Hello"),
            ]
        )

        service.complete(request)

        call_args = mock_client.create_chat_completion.call_args
        messages_arg = call_args[1]["messages"]
        assert messages_arg == [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]
