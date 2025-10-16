"""Конфигурация приложения с валидацией через Pydantic."""

from pydantic import Field, PositiveFloat, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Конфигурация Telegram бота с LLM интеграцией."""

    # Обязательные параметры
    telegram_bot_token: str = Field(..., min_length=1, description="Telegram Bot API token")
    openrouter_api_key: str = Field(..., min_length=1, description="OpenRouter API key")
    database_url: str = Field(..., min_length=1, description="PostgreSQL connection string")

    # Опциональные параметры LLM
    llm_model: str = Field(
        default="openai/gpt-oss-20b:free",
        min_length=1,
        description="LLM model identifier",
    )
    llm_temperature: PositiveFloat = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM temperature (0.0-2.0)",
    )
    llm_max_tokens: PositiveInt = Field(
        default=1000,
        ge=1,
        le=100000,
        description="Maximum tokens in LLM response",
    )
    llm_timeout: PositiveInt = Field(
        default=30, ge=1, le=300, description="LLM API timeout in seconds"
    )

    # Параметры истории диалогов
    max_history_messages: PositiveInt = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of messages in conversation history",
    )

    # Системный промпт
    system_prompt_path: str = Field(
        default="prompts/nutritionist.txt",
        min_length=1,
        description="Path to system prompt file",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
