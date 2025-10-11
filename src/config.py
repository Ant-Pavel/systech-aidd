import os

from dotenv import load_dotenv


class Config:
    def __init__(self) -> None:
        load_dotenv()

        # Обязательные параметры
        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

        # Валидация обязательных параметров
        if not telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY не найден в .env")

        # Присваиваем валидированные значения
        self.telegram_bot_token: str = telegram_bot_token
        self.openrouter_api_key: str = openrouter_api_key

        # Опциональные параметры LLM (значения по умолчанию)
        self.llm_model: str = os.getenv("LLM_MODEL", "openai/gpt-oss-20b:free")
        self.llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
        self.llm_timeout: int = int(os.getenv("LLM_TIMEOUT", "30"))

        # Параметры истории диалогов
        self.max_history_messages: int = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))
