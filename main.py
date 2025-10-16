import asyncio
import logging

from src.bot import TelegramBot
from src.command_handler import CommandHandler
from src.config import Config
from src.database import close_pool, init_db
from src.database_conversation import DatabaseConversation
from src.llm_client import LLMClient
from src.message_handler import MessageHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    config = Config()

    try:
        # Инициализируем подключение к БД
        logger.info("Initializing database connection...")
        await init_db(config.database_url)
        logger.info("Database connection initialized successfully")

        # Инициализируем LLM клиент
        llm_client = LLMClient(
            api_key=config.openrouter_api_key,
            model=config.llm_model,
            temperature=config.llm_temperature,
            max_tokens=config.llm_max_tokens,
            timeout=config.llm_timeout,
            system_prompt_path=config.system_prompt_path,
        )

        # Инициализируем хранилище истории диалогов (PostgreSQL)
        conversation = DatabaseConversation(config.max_history_messages)

        # Инициализируем обработчик команд
        command_handler = CommandHandler(conversation)

        # Инициализируем обработчик сообщений
        message_handler = MessageHandler(llm_client, conversation)

        # Инициализируем бота
        bot = TelegramBot(config.telegram_bot_token, command_handler, message_handler)

        logger.info("Starting Telegram bot...")
        await bot.start()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        # Graceful shutdown - закрываем connection pool
        logger.info("Closing database connection...")
        await close_pool()
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
