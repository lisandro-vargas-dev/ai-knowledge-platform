"""Application configuration loaded from environment variables.

Uses pydantic-settings for typed, validated configuration.
All LLM provider settings are read from environment variables
or a .env file, never hard-coded.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    # --- General ---
    app_name: str = "AI Knowledge Platform Backend"
    debug: bool = False

    # --- LLM provider ---
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key. Required for real provider calls.",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Default model identifier sent to OpenAI.",
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for the OpenAI-compatible API.",
    )
    openai_timeout_seconds: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="HTTP timeout in seconds for provider requests.",
    )
    openai_max_retries: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Maximum automatic retries on transient errors.",
    )
    openai_max_tokens: int = Field(
        default=1024,
        ge=1,
        le=128_000,
        description="Default max_tokens sent to the provider.",
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default sampling temperature.",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()
