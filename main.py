import asyncio
import logging
from src.config import Config
from src.bot import TelegramBot


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def main():
    config = Config()
    bot = TelegramBot(config.telegram_bot_token)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())

