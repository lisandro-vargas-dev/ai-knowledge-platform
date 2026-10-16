"""Custom exception types for LLM integration errors.

These exceptions provide structured error information that the
API layer translates into appropriate HTTP responses.
"""

from __future__ import annotations


class LLMError(Exception):
    """Base exception for LLM-related errors."""

    def __init__(self, message: str, *, detail: str | None = None) -> None:
        super().__init__(message)
        self.detail = detail


class LLMAuthenticationError(LLMError):
    """Raised when the API key is missing or invalid."""


class LLMRateLimitError(LLMError):
    """Raised when the provider returns a rate-limit response."""


class LLMTimeoutError(LLMError):
    """Raised when a provider request times out."""


class LLMProviderError(LLMError):
    """Raised for unexpected provider-side errors (5xx, etc.)."""


class LLMInvalidRequestError(LLMError):
    """Raised when the provider rejects the request payload."""
