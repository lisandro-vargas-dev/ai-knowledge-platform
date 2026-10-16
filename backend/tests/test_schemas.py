"""Unit tests for app.schemas — request/response validation."""

import pytest
from pydantic import ValidationError

from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ErrorResponse,
    UsageInfo,
)


class TestChatMessage:
    """Validate ChatMessage constraints."""

    def test_valid_roles(self) -> None:
        for role in ("system", "user", "assistant"):
            msg = ChatMessage(role=role, content="hello")
            assert msg.role == role

    def test_invalid_role_rejected(self) -> None:
        with pytest.raises(ValidationError, match="String should match pattern"):
            ChatMessage(role="admin", content="hello")

    def test_empty_content_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ChatMessage(role="user", content="")

    def test_content_too_long_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ChatMessage(role="user", content="x" * 100_001)


class TestChatCompletionRequest:
    """Validate incoming request constraints."""

    def test_valid_minimal_request(self) -> None:
        req = ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Hi")]
        )
        assert len(req.messages) == 1
        assert req.model is None
        assert req.temperature is None
        assert req.max_tokens is None

    def test_request_with_overrides(self) -> None:
        req = ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Hi")],
            model="gpt-4o",
            temperature=0.5,
            max_tokens=512,
        )
        assert req.model == "gpt-4o"
        assert req.temperature == 0.5
        assert req.max_tokens == 512

    def test_empty_messages_rejected(self) -> None:
        with pytest.raises(ValidationError, match="too_short"):
            ChatCompletionRequest(messages=[])

    def test_temperature_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                messages=[ChatMessage(role="user", content="Hi")],
                temperature=3.0,
            )

    def test_max_tokens_zero_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                messages=[ChatMessage(role="user", content="Hi")],
                max_tokens=0,
            )


class TestChatCompletionResponse:
    """Validate response construction."""

    def test_response_without_usage(self) -> None:
        resp = ChatCompletionResponse(
            message="Hello!",
            model="gpt-4o-mini",
        )
        assert resp.message == "Hello!"
        assert resp.model == "gpt-4o-mini"
        assert resp.usage is None

    def test_response_with_usage(self) -> None:
        resp = ChatCompletionResponse(
            message="Hi",
            model="gpt-4o",
            usage=UsageInfo(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )
        assert resp.usage is not None
        assert resp.usage.total_tokens == 15


class TestErrorResponse:
    """Validate error response schema."""

    def test_error_with_detail(self) -> None:
        err = ErrorResponse(error="Something failed", detail="details here")
        assert err.error == "Something failed"
        assert err.detail == "details here"

    def test_error_without_detail(self) -> None:
        err = ErrorResponse(error="fail")
        assert err.detail is None
