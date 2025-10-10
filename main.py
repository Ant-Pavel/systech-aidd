import asyncio
import logging
from src.config import Config
from src.llm_client import LLMClient
from src.message_handler import MessageHandler
from src.bot import TelegramBot


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def main():
    config = Config()
    
    # Инициализируем LLM клиент
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        model=config.llm_model,
        temperature=config.llm_temperature,
        max_tokens=config.llm_max_tokens,
        timeout=config.llm_timeout
    )
    
    # Инициализируем обработчик сообщений
    message_handler = MessageHandler(llm_client)
    
    # Инициализируем бота
    bot = TelegramBot(config.telegram_bot_token, message_handler)
    
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())

