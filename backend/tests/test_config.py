"""Unit tests for app.config."""

import os

from app.config import Settings


class TestSettings:
    """Test configuration loading from environment variables."""

    def test_defaults(self) -> None:
        """Settings should have sensible defaults when no env vars are set."""
        settings = Settings(
            _env_file=None,  # type: ignore[call-arg]
        )
        assert settings.openai_api_key == ""
        assert settings.openai_model == "gpt-4o-mini"
        assert settings.openai_base_url == "https://api.openai.com/v1"
        assert settings.openai_timeout_seconds == 30.0
        assert settings.openai_max_retries == 2
        assert settings.openai_max_tokens == 1024
        assert settings.openai_temperature == 0.7
        assert settings.debug is False

    def test_env_override(self, monkeypatch) -> None:
        """Settings should pick up values from environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "60")
        monkeypatch.setenv("OPENAI_MAX_RETRIES", "5")
        monkeypatch.setenv("OPENAI_MAX_TOKENS", "2048")
        monkeypatch.setenv("OPENAI_TEMPERATURE", "0.3")
        monkeypatch.setenv("DEBUG", "true")

        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        assert settings.openai_api_key == "sk-test-key"
        assert settings.openai_model == "gpt-4o"
        assert settings.openai_timeout_seconds == 60.0
        assert settings.openai_max_retries == 5
        assert settings.openai_max_tokens == 2048
        assert settings.openai_temperature == 0.3
        assert settings.debug is True

    def test_extra_vars_ignored(self, monkeypatch) -> None:
        """Unknown environment variables should be silently ignored."""
        monkeypatch.setenv("TOTALLY_UNKNOWN_VAR", "whatever")
        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        assert not hasattr(settings, "totally_unknown_var")
