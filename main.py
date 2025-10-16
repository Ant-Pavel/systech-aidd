import asyncio
import logging

from src.bot import TelegramBot
from src.command_handler import CommandHandler
from src.config import Config
from src.conversation import Conversation
from src.llm_client import LLMClient
from src.message_handler import MessageHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main() -> None:
    config = Config()

    # Инициализируем LLM клиент
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        model=config.llm_model,
        temperature=config.llm_temperature,
        max_tokens=config.llm_max_tokens,
        timeout=config.llm_timeout,
        system_prompt_path=config.system_prompt_path,
    )

    # Инициализируем хранилище истории диалогов
    conversation = Conversation(config.max_history_messages)

    # Инициализируем обработчик команд
    command_handler = CommandHandler(conversation)

    # Инициализируем обработчик сообщений
    message_handler = MessageHandler(llm_client, conversation)

    # Инициализируем бота
    bot = TelegramBot(config.telegram_bot_token, command_handler, message_handler)

    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
