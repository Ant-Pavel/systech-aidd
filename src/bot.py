"""Telegram бот - управление и регистрация обработчиков."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message

from src.command_handler import CommandHandler
from src.message_handler import MessageHandler

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram бот - координация bot/dispatcher и регистрация обработчиков."""

    def __init__(
        self, token: str, command_handler: CommandHandler, message_handler: MessageHandler
    ) -> None:
        self.bot: Bot = Bot(token=token)
        self.dp: Dispatcher = Dispatcher()
        self.command_handler: CommandHandler = command_handler
        self.message_handler: MessageHandler = message_handler
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Регистрация обработчиков команд и сообщений."""
        self.dp.message(Command("start"))(self.command_handler.start)
        self.dp.message(Command("help"))(self.command_handler.help)
        self.dp.message(Command("clear"))(self.command_handler.clear)
        self.dp.message()(self._handle_text_message)

    async def _handle_text_message(self, message: Message) -> None:
        """Обработка текстового сообщения с индикатором печати."""
        try:
            # Проверяем наличие обязательных полей
            if message.from_user is None or message.text is None:
                return

            # Показываем индикатор "печатает..."
            await self.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

            # Обрабатываем сообщение через MessageHandler
            response = await self.message_handler.handle_message(
                user_id=message.from_user.id, chat_id=message.chat.id, text=message.text
            )

            # Отправляем ответ
            await message.answer(response)

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await message.answer("Извините, произошла ошибка. Попробуйте еще раз.")

    async def start(self) -> None:
        """Запуск бота в режиме polling."""
        logger.info("Bot started successfully")
        await self.dp.start_polling(self.bot)
