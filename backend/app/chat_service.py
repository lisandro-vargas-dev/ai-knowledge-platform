"""Chat completion service layer.

Orchestrates the flow between validated API requests, the LLM client,
and structured API responses.  This module owns the business logic
but not HTTP concerns.
"""

from __future__ import annotations

import logging

from openai.types.chat import ChatCompletion

from app.llm_client import OpenAIClient
from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    UsageInfo,
)

logger = logging.getLogger(__name__)


class ChatService:
    """Stateless service that processes chat completion requests."""

    def __init__(self, client: OpenAIClient) -> None:
        self._client = client

    def complete(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Execute a chat completion and return a structured response.

        Parameters
        ----------
        request:
            Validated incoming request with messages and optional overrides.

        Returns
        -------
        ChatCompletionResponse
            The assistant's message, resolved model name, and usage info.
        """
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        completion: ChatCompletion = self._client.create_chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Extract the assistant message text.
        choice = completion.choices[0]
        assistant_text = choice.message.content or ""

        # Build usage info when the provider supplies it.
        usage: UsageInfo | None = None
        if completion.usage:
            usage = UsageInfo(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens,
            )

        return ChatCompletionResponse(
            message=assistant_text,
            model=completion.model,
            usage=usage,
        )
