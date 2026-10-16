"""OpenAI API client wrapper.

Encapsulates HTTP communication with the OpenAI-compatible API,
including timeout, retry, error classification, and usage logging.

This module depends only on the ``openai`` SDK and application
configuration — it does not know about FastAPI or HTTP endpoints.
"""

from __future__ import annotations

import logging
from typing import Any

import openai
from openai.types.chat import ChatCompletion

from app.config import Settings
from app.exceptions import (
    LLMAuthenticationError,
    LLMInvalidRequestError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Thin wrapper around the OpenAI Python SDK.

    Responsibilities:
    - Build and hold a configured ``openai.OpenAI`` instance.
    - Translate SDK exceptions into application-level exceptions.
    - Log usage information when available.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = openai.OpenAI(
            api_key=settings.openai_api_key or "sk-placeholder-not-a-real-key",
            base_url=settings.openai_base_url,
            timeout=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )

    def create_chat_completion(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatCompletion:
        """Send a chat completion request to the provider.

        Parameters
        ----------
        messages:
            List of ``{"role": ..., "content": ...}`` dicts.
        model:
            Model identifier override; falls back to configured default.
        temperature:
            Sampling temperature override.
        max_tokens:
            Maximum tokens override.

        Returns
        -------
        ChatCompletion
            The parsed provider response.

        Raises
        ------
        LLMAuthenticationError
            API key missing or rejected.
        LLMRateLimitError
            Rate limit or quota exceeded.
        LLMTimeoutError
            Request timed out.
        LLMInvalidRequestError
            The provider rejected the request payload.
        LLMProviderError
            Unexpected provider-side error.
        """
        resolved_model = model or self._settings.openai_model
        resolved_temperature = (
            temperature if temperature is not None else self._settings.openai_temperature
        )
        resolved_max_tokens = max_tokens or self._settings.openai_max_tokens

        params: dict[str, Any] = {
            "model": resolved_model,
            "messages": messages,
            "temperature": resolved_temperature,
            "max_tokens": resolved_max_tokens,
        }

        logger.info(
            "Sending chat completion request: model=%s, messages=%d, "
            "temperature=%.2f, max_tokens=%d",
            resolved_model,
            len(messages),
            resolved_temperature,
            resolved_max_tokens,
        )

        try:
            response = self._client.chat.completions.create(**params)
        except openai.AuthenticationError as exc:
            logger.error("Authentication failed: %s", exc)
            raise LLMAuthenticationError(
                "Invalid or missing API key.",
                detail=str(exc),
            ) from exc
        except openai.RateLimitError as exc:
            logger.warning("Rate limit hit: %s", exc)
            raise LLMRateLimitError(
                "Rate limit exceeded. Try again later.",
                detail=str(exc),
            ) from exc
        except openai.APITimeoutError as exc:
            logger.warning("Request timed out: %s", exc)
            raise LLMTimeoutError(
                "Provider request timed out.",
                detail=str(exc),
            ) from exc
        except openai.BadRequestError as exc:
            logger.error("Invalid request: %s", exc)
            raise LLMInvalidRequestError(
                "The provider rejected the request.",
                detail=str(exc),
            ) from exc
        except openai.APIStatusError as exc:
            logger.error("Provider error (status %s): %s", exc.status_code, exc)
            raise LLMProviderError(
                f"Provider returned status {exc.status_code}.",
                detail=str(exc),
            ) from exc
        except openai.APIConnectionError as exc:
            logger.error("Connection error: %s", exc)
            raise LLMProviderError(
                "Could not connect to the provider.",
                detail=str(exc),
            ) from exc

        # Log usage when the provider includes it.
        if response.usage:
            logger.info(
                "Usage — prompt: %d, completion: %d, total: %d tokens",
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                response.usage.total_tokens,
            )

        return response
