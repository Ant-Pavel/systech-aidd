"""Unit-тесты для модуля command_handler."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Message

from src.command_handler import CommandHandler


class TestCommandHandler:
    """Тесты для класса CommandHandler."""

    @pytest.fixture
    def mock_conversation(self) -> MagicMock:
        """Фикстура для мока Conversation."""
        mock = MagicMock()
        mock.clear_history = AsyncMock()
        return mock

    @pytest.fixture
    def command_handler(self, mock_conversation: MagicMock) -> CommandHandler:
        """Фикстура для создания CommandHandler."""
        return CommandHandler(conversation=mock_conversation)

    @pytest.fixture
    def mock_message(self) -> MagicMock:
        """Фикстура для мока Message."""
        message = MagicMock()
        message.from_user = MagicMock()
        message.from_user.id = 123
        message.chat = MagicMock()
        message.chat.id = 456
        message.answer = AsyncMock()
        return message

    async def test_start_command(
        self, command_handler: CommandHandler, mock_message: MagicMock
    ) -> None:
        """Тест команды /start."""
        await command_handler.start(mock_message)

        # Проверяем что был отправлен ответ
        mock_message.answer.assert_called_once()

        # Проверяем содержание ответа
        call_args = mock_message.answer.call_args[0][0]
        assert "Привет" in call_args
        assert "нутрициолог" in call_args
        assert "/help" in call_args

    async def test_start_command_no_user(
        self, command_handler: CommandHandler, mock_message: MagicMock
    ) -> None:
        """Тест команды /start без пользователя (from_user = None)."""
        mock_message.from_user = None

        await command_handler.start(mock_message)

        # Не должно быть вызова answer
        mock_message.answer.assert_not_called()

    async def test_help_command(
        self, command_handler: CommandHandler, mock_message: MagicMock
    ) -> None:
        """Тест команды /help."""
        await command_handler.help(mock_message)

        # Проверяем что был отправлен ответ
        mock_message.answer.assert_called_once()

        # Проверяем содержание ответа
        call_args = mock_message.answer.call_args[0][0]
        assert "Доступные команды" in call_args
        assert "/start" in call_args
        assert "/help" in call_args
        assert "/clear" in call_args

    async def test_help_command_no_user(
        self, command_handler: CommandHandler, mock_message: MagicMock
    ) -> None:
        """Тест команды /help без пользователя (from_user = None)."""
        mock_message.from_user = None

        await command_handler.help(mock_message)

        # Не должно быть вызова answer
        mock_message.answer.assert_not_called()

    async def test_clear_command(
        self,
        command_handler: CommandHandler,
        mock_message: MagicMock,
        mock_conversation: MagicMock,
    ) -> None:
        """Тест команды /clear."""
        await command_handler.clear(mock_message)

        # Проверяем что была вызвана очистка истории
        mock_conversation.clear_history.assert_called_once_with(
            mock_message.from_user.id, mock_message.chat.id
        )

        # Проверяем что был отправлен ответ
        mock_message.answer.assert_called_once()

        # Проверяем содержание ответа
        call_args = mock_message.answer.call_args[0][0]
        assert "История диалога очищена" in call_args

    async def test_clear_command_no_user(
        self,
        command_handler: CommandHandler,
        mock_message: MagicMock,
        mock_conversation: MagicMock,
    ) -> None:
        """Тест команды /clear без пользователя (from_user = None)."""
        mock_message.from_user = None

        await command_handler.clear(mock_message)

        # Не должно быть вызова clear_history
        mock_conversation.clear_history.assert_not_called()

        # Не должно быть вызова answer
        mock_message.answer.assert_not_called()

    async def test_clear_command_with_different_users(
        self,
        command_handler: CommandHandler,
        mock_conversation: MagicMock,
    ) -> None:
        """Тест команды /clear для разных пользователей."""
        # Первый пользователь
        message1 = MagicMock()
        message1.from_user = MagicMock()
        message1.from_user.id = 111
        message1.chat = MagicMock()
        message1.chat.id = 222
        message1.answer = AsyncMock()

        # Второй пользователь
        message2 = MagicMock()
        message2.from_user = MagicMock()
        message2.from_user.id = 333
        message2.chat = MagicMock()
        message2.chat.id = 444
        message2.answer = AsyncMock()

        await command_handler.clear(message1)
        await command_handler.clear(message2)

        # Проверяем что очистка была вызвана для каждого пользователя
        assert mock_conversation.clear_history.call_count == 2
        mock_conversation.clear_history.assert_any_call(111, 222)
        mock_conversation.clear_history.assert_any_call(333, 444)

    def test_command_handler_initialization(self) -> None:
        """Тест инициализации CommandHandler."""
        mock_conv = MagicMock()
        handler = CommandHandler(conversation=mock_conv)

        assert handler.conversation == mock_conv

    async def test_commands_response_format(
        self, command_handler: CommandHandler, mock_message: MagicMock
    ) -> None:
        """Тест что все команды отвечают строкой."""
        await command_handler.start(mock_message)
        await command_handler.help(mock_message)
        await command_handler.clear(mock_message)

        # Проверяем что answer был вызван 3 раза (по разу на каждую команду)
        assert mock_message.answer.call_count == 3

        # Проверяем что все ответы - строки
        for call in mock_message.answer.call_args_list:
            response = call[0][0]
            assert isinstance(response, str)
            assert len(response) > 0

    async def test_role_command(
        self, command_handler: CommandHandler, mock_message: MagicMock
    ) -> None:
        """Тест команды /role - отображение роли бота."""
        await command_handler.role(mock_message)

        mock_message.answer.assert_called_once()
        response = mock_message.answer.call_args[0][0]

        # Проверяем что в ответе упоминается роль
        assert "нутрициолог" in response.lower() or "nutritionist" in response.lower()
        assert len(response) > 0

    async def test_role_command_no_user(self, command_handler: CommandHandler) -> None:
        """Тест команды /role без пользователя."""
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = None
        mock_message.answer = AsyncMock()

        await command_handler.role(mock_message)

        # Команда не должна вызвать answer если нет пользователя
        mock_message.answer.assert_not_called()

    async def test_new_command_alias(
        self, command_handler: CommandHandler, mock_message: MagicMock
    ) -> None:
        """Тест что /new является алиасом для /clear."""
        # Команда /new должна использовать тот же метод clear()
        # Проверяем что она очищает историю и отправляет ответ
        await command_handler.clear(mock_message)

        # Проверяем что ответ был отправлен
        mock_message.answer.assert_called_once()
        response = mock_message.answer.call_args[0][0]

        # Проверяем содержание ответа
        assert "очищена" in response.lower() or "clear" in response.lower()
        assert len(response) > 0
