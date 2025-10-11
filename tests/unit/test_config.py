"""Unit-тесты для модуля config."""

import pytest
from pydantic import ValidationError

from src.config import Config


class TestConfig:
    """Тесты для класса Config."""

    def test_config_with_valid_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест создания Config с валидными данными."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token_123")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key_123")
        monkeypatch.setenv("LLM_MODEL", "gpt-4")
        monkeypatch.setenv("LLM_TEMPERATURE", "0.8")
        monkeypatch.setenv("LLM_MAX_TOKENS", "2000")
        monkeypatch.setenv("LLM_TIMEOUT", "60")
        monkeypatch.setenv("MAX_HISTORY_MESSAGES", "15")

        config = Config()

        assert config.telegram_bot_token == "test_token_123"
        assert config.openrouter_api_key == "test_key_123"
        assert config.llm_model == "gpt-4"
        assert config.llm_temperature == 0.8
        assert config.llm_max_tokens == 2000
        assert config.llm_timeout == 60
        assert config.max_history_messages == 15

    def test_config_with_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест создания Config с дефолтными значениями."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")

        config = Config()

        assert config.telegram_bot_token == "test_token"
        assert config.openrouter_api_key == "test_key"
        # Проверяем дефолтные значения
        assert config.llm_model == "openai/gpt-oss-20b:free"
        assert config.llm_temperature == 0.7
        assert config.llm_max_tokens == 1000
        assert config.llm_timeout == 30
        assert config.max_history_messages == 10

    def test_config_missing_telegram_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест ошибки при отсутствии TELEGRAM_BOT_TOKEN."""
        # Отключаем чтение .env файла
        monkeypatch.setattr(
            "pydantic_settings.sources.DotEnvSettingsSource.__call__", lambda *args, **kwargs: {}
        )

        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        # Убеждаемся что TELEGRAM_BOT_TOKEN не установлен
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

        with pytest.raises(ValidationError) as exc_info:
            Config()

        assert "telegram_bot_token" in str(exc_info.value).lower()

    def test_config_missing_openrouter_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест ошибки при отсутствии OPENROUTER_API_KEY."""
        # Отключаем чтение .env файла
        monkeypatch.setattr(
            "pydantic_settings.sources.DotEnvSettingsSource.__call__", lambda *args, **kwargs: {}
        )

        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        with pytest.raises(ValidationError) as exc_info:
            Config()

        assert "openrouter_api_key" in str(exc_info.value).lower()

    def test_config_empty_telegram_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест ошибки при пустом TELEGRAM_BOT_TOKEN."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")

        with pytest.raises(ValidationError) as exc_info:
            Config()

        assert "telegram_bot_token" in str(exc_info.value).lower()

    def test_config_temperature_too_high(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест ошибки при temperature > 2.0."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("LLM_TEMPERATURE", "2.5")

        with pytest.raises(ValidationError) as exc_info:
            Config()

        assert "llm_temperature" in str(exc_info.value).lower()

    def test_config_temperature_negative(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест ошибки при отрицательном temperature."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("LLM_TEMPERATURE", "-0.5")

        with pytest.raises(ValidationError) as exc_info:
            Config()

        assert "llm_temperature" in str(exc_info.value).lower()

    def test_config_max_tokens_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест ошибки при max_tokens = 0."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("LLM_MAX_TOKENS", "0")

        with pytest.raises(ValidationError) as exc_info:
            Config()

        assert "llm_max_tokens" in str(exc_info.value).lower()

    def test_config_max_tokens_too_large(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест ошибки при max_tokens > 100000."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("LLM_MAX_TOKENS", "150000")

        with pytest.raises(ValidationError) as exc_info:
            Config()

        assert "llm_max_tokens" in str(exc_info.value).lower()

    def test_config_type_conversion_string_to_int(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест автоматического приведения str -> int."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("LLM_MAX_TOKENS", "5000")  # str
        monkeypatch.setenv("MAX_HISTORY_MESSAGES", "20")  # str

        config = Config()

        assert isinstance(config.llm_max_tokens, int)
        assert config.llm_max_tokens == 5000
        assert isinstance(config.max_history_messages, int)
        assert config.max_history_messages == 20

    def test_config_type_conversion_string_to_float(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест автоматического приведения str -> float."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("LLM_TEMPERATURE", "1.5")  # str

        config = Config()

        assert isinstance(config.llm_temperature, float)
        assert config.llm_temperature == 1.5

    def test_config_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест case-insensitive загрузки переменных окружения."""
        monkeypatch.setenv("telegram_bot_token", "test_token")  # lowercase
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")

        config = Config()

        assert config.telegram_bot_token == "test_token"
        assert config.openrouter_api_key == "test_key"

    def test_config_system_prompt_path_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест дефолтного значения system_prompt_path."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")

        config = Config()

        assert config.system_prompt_path == "prompts/nutritionist.txt"

    def test_config_system_prompt_path_custom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест переопределения system_prompt_path через переменную окружения."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("SYSTEM_PROMPT_PATH", "custom/path/prompt.txt")

        config = Config()

        assert config.system_prompt_path == "custom/path/prompt.txt"
