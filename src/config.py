import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        
        # Обязательные параметры
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Валидация
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")

