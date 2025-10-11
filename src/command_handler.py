"""Обработчик команд бота."""

import logging

from aiogram.types import Message

from src.protocols import ConversationStorageProtocol

logger = logging.getLogger(__name__)


class CommandHandler:
    """Обработчик команд бота."""

    def __init__(self, conversation: ConversationStorageProtocol) -> None:
        self.conversation: ConversationStorageProtocol = conversation

    async def start(self, message: Message) -> None:
        """Команда /start - приветствие."""
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

    async def help(self, message: Message) -> None:
        """Команда /help - справка."""
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

    async def clear(self, message: Message) -> None:
        """Команда /clear - очистка истории."""
        if message.from_user is None:
            return
        logger.info(f"Command /clear from user {message.from_user.id} in chat {message.chat.id}")
        self.conversation.clear_history(message.from_user.id, message.chat.id)
        await message.answer("✅ История диалога очищена. Начнём с чистого листа!")
