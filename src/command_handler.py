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
            "👋 Привет! Я твой персональный нутрициолог на базе искусственного интеллекта.\n\n"
            "Я помогу тебе с:\n"
            "• Консультациями по вопросам питания\n"
            "• Составлением рационов\n"
            "• Выбором продуктов\n"
            "• Ответами на вопросы о диетах\n"
            "• Разбором состава продуктов\n\n"
            "Просто напиши мне свой вопрос, и я отвечу!\n\n"
            "Используй /help чтобы узнать доступные команды "
            "или /role чтобы узнать больше о моих возможностях."
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
            "/role - Узнать о моей роли и возможностях\n"
            "/clear или /new - Очистить историю диалога\n\n"
            "💬 Просто отправь мне текстовое сообщение с вопросом о питании, и я отвечу!\n"
            "Я помню последние 10 сообщений нашего разговора для контекста."
        )
        await message.answer(help_text)

    async def clear(self, message: Message) -> None:
        """Команда /clear - очистка истории."""
        if message.from_user is None:
            return
        logger.info(f"Command /clear from user {message.from_user.id} in chat {message.chat.id}")
        self.conversation.clear_history(message.from_user.id, message.chat.id)
        await message.answer("✅ История диалога очищена. Начнём с чистого листа!")

    async def role(self, message: Message) -> None:
        """Команда /role - отображение роли бота."""
        if message.from_user is None:
            return
        logger.info(f"Command /role from user {message.from_user.id}")
        role_text = (
            "👨‍⚕️ Моя роль: Профессиональный нутрициолог\n\n"
            "Я помогу тебе с:\n"
            "• Консультациями по вопросам питания\n"
            "• Составлением сбалансированных рационов\n"
            "• Рекомендациями по выбору продуктов\n"
            "• Объяснением пользы и вреда различных продуктов\n"
            "• Ответами на вопросы о диетах и системах питания\n"
            "• Разбором состава продуктов и этикеток\n"
            "• Советами по режиму питания\n\n"
            "Я основываюсь на научных данных и доказательной медицине. "
            "При серьезных проблемах со здоровьем рекомендую консультацию врача."
        )
        await message.answer(role_text)
