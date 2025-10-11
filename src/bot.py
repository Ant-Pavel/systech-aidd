import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message

from src.conversation import Conversation
from src.message_handler import MessageHandler

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(
        self, token: str, message_handler: MessageHandler, conversation: Conversation
    ) -> None:
        self.bot: Bot = Bot(token=token)
        self.dp: Dispatcher = Dispatcher()
        self.message_handler: MessageHandler = message_handler
        self.conversation: Conversation = conversation
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("clear"))(self.cmd_clear)
        self.dp.message()(self.handle_text_message)

    async def cmd_start(self, message: Message) -> None:
        if message.from_user is None:
            return
        logger.info(f"Command /start from user {message.from_user.id}")
        welcome_text = (
            "👋 Привет! Я AI ассистент на базе LLM.\n\n"
            "Я могу помочь тебе с:\n"
            "• Ответами на вопросы\n"
            "• Генерацией идей\n"
            "• Объяснением сложных тем\n"
            "• Поддержкой в диалоге\n\n"
            "Просто напиши мне что-нибудь, и я отвечу!\n\n"
            "Используй /help чтобы узнать доступные команды."
        )
        await message.answer(welcome_text)

    async def cmd_help(self, message: Message) -> None:
        if message.from_user is None:
            return
        logger.info(f"Command /help from user {message.from_user.id}")
        help_text = (
            "📋 Доступные команды:\n\n"
            "/start - Показать приветственное сообщение\n"
            "/help - Показать это сообщение\n"
            "/clear - Очистить историю диалога\n\n"
            "💬 Просто отправь мне текстовое сообщение, и я отвечу!\n"
            "Я помню последние 10 сообщений нашего разговора."
        )
        await message.answer(help_text)

    async def cmd_clear(self, message: Message) -> None:
        if message.from_user is None:
            return
        logger.info(f"Command /clear from user {message.from_user.id} in chat {message.chat.id}")
        self.conversation.clear_history(message.from_user.id, message.chat.id)
        await message.answer("✅ История диалога очищена. Начнём с чистого листа!")

    async def handle_text_message(self, message: Message) -> None:
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
        logger.info("Bot started successfully")
        await self.dp.start_polling(self.bot)
