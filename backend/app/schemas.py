"""Pydantic schemas for LLM chat completion requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: str = Field(
        ...,
        pattern=r"^(system|user|assistant)$",
        description="Message role: system, user, or assistant.",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=100_000,
        description="Message text content.",
    )


class ChatCompletionRequest(BaseModel):
    """Incoming chat completion request."""

    messages: list[ChatMessage] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Conversation messages. At least one message is required.",
    )
    model: str | None = Field(
        default=None,
        description="Model override. Uses the configured default when omitted.",
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature override.",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        le=128_000,
        description="Max tokens override.",
    )


class UsageInfo(BaseModel):
    """Token usage information returned by the provider."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    """Response returned by the chat completion endpoint."""

    message: str = Field(
        ...,
        description="The assistant's response text.",
    )
    model: str = Field(
        ...,
        description="The model that generated the response.",
    )
    usage: UsageInfo | None = Field(
        default=None,
        description="Token usage information, when available.",
    )


class ErrorResponse(BaseModel):
    """Standard error response body."""

    error: str
    detail: str | None = None
