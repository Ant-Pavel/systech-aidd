"""Fixtures для тестов."""

import pytest


@pytest.fixture
def sample_config_data() -> dict[str, str]:
    """Пример данных конфигурации для тестов."""
    return {
        "TELEGRAM_BOT_TOKEN": "test_token_123",
        "OPENROUTER_API_KEY": "test_key_123",
        "LLM_MODEL": "gpt-3.5-turbo",
        "LLM_TEMPERATURE": "0.7",
        "LLM_MAX_TOKENS": "1000",
        "MAX_HISTORY_MESSAGES": "10",
    }
