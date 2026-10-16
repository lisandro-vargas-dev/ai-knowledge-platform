"""FastAPI application entry point.

Defines the application instance, dependency wiring, API endpoints,
and exception handlers.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.chat_service import ChatService
from app.config import Settings, get_settings
from app.exceptions import (
    LLMAuthenticationError,
    LLMError,
    LLMInvalidRequestError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.llm_client import OpenAIClient
from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application-scoped singletons (created at startup, torn down at shutdown)
# ---------------------------------------------------------------------------

_chat_service: ChatService | None = None


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage application-scoped resources."""
    global _chat_service  # noqa: PLW0603
    settings = get_settings()

    log_level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    client = OpenAIClient(settings)
    _chat_service = ChatService(client)
    logger.info(
        "LLM client initialised — model=%s, base_url=%s, timeout=%.0fs, retries=%d",
        settings.openai_model,
        settings.openai_base_url,
        settings.openai_timeout_seconds,
        settings.openai_max_retries,
    )
    yield
    _chat_service = None
    logger.info("Application shutdown complete.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Knowledge Platform Backend",
    version="0.2.0",
    description="Backend API for the AI Knowledge Platform",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


def _get_chat_service() -> ChatService:
    """FastAPI dependency that returns the application ChatService."""
    if _chat_service is None:
        raise HTTPException(
            status_code=503,
            detail="LLM service not available. The application may still be starting.",
        )
    return _chat_service


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(LLMAuthenticationError)
async def _handle_auth_error(
    request: Request, exc: LLMAuthenticationError
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content=ErrorResponse(error=str(exc), detail=exc.detail).model_dump(),
    )


@app.exception_handler(LLMRateLimitError)
async def _handle_rate_limit(
    request: Request, exc: LLMRateLimitError
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(error=str(exc), detail=exc.detail).model_dump(),
    )


@app.exception_handler(LLMTimeoutError)
async def _handle_timeout(
    request: Request, exc: LLMTimeoutError
) -> JSONResponse:
    return JSONResponse(
        status_code=504,
        content=ErrorResponse(error=str(exc), detail=exc.detail).model_dump(),
    )


@app.exception_handler(LLMInvalidRequestError)
async def _handle_invalid_request(
    request: Request, exc: LLMInvalidRequestError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(error=str(exc), detail=exc.detail).model_dump(),
    )


@app.exception_handler(LLMError)
async def _handle_llm_error(
    request: Request, exc: LLMError
) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content=ErrorResponse(error=str(exc), detail=exc.detail).model_dump(),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return application health status."""
    return HealthResponse(status="ok")


@app.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication error"},
        422: {"model": ErrorResponse, "description": "Invalid request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        502: {"model": ErrorResponse, "description": "Provider error"},
        504: {"model": ErrorResponse, "description": "Provider timeout"},
    },
)
def create_chat_completion(
    body: ChatCompletionRequest,
    service: ChatService = Depends(_get_chat_service),
) -> ChatCompletionResponse:
    """Generate a chat completion via the configured LLM provider.

    Accepts a list of conversation messages and returns the assistant's
    response along with model identification and token usage.
    """
    return service.complete(body)
