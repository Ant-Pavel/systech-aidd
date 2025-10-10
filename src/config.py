import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        
        # Обязательные параметры
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Валидация обязательных параметров
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY не найден в .env")
        
        # Опциональные параметры LLM (значения по умолчанию)
        self.llm_model = os.getenv("LLM_MODEL", "openai/gpt-oss-20b:free")
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
        self.llm_timeout = int(os.getenv("LLM_TIMEOUT", "30"))

