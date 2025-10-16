"""Unit-тесты для модуля message_handler."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.message_handler import MessageHandler
from src.types import ChatMessage


class TestMessageHandler:
    """Тесты для класса MessageHandler."""

    @pytest.fixture
    def mock_llm_client(self) -> MagicMock:
        """Фикстура для мока LLMClient."""
        mock = MagicMock()
        mock.get_response = AsyncMock()
        return mock

    @pytest.fixture
    def mock_conversation(self) -> MagicMock:
        """Фикстура для мока Conversation."""
        mock = MagicMock()
        mock.get_history = AsyncMock(return_value=[])
        mock.add_message = AsyncMock()
        mock.clear_history = AsyncMock()
        return mock

    @pytest.fixture
    def message_handler(
        self, mock_llm_client: MagicMock, mock_conversation: MagicMock
    ) -> MessageHandler:
        """Фикстура для создания MessageHandler."""
        return MessageHandler(llm_client=mock_llm_client, conversation=mock_conversation)

    async def test_handle_message_success(
        self,
        message_handler: MessageHandler,
        mock_llm_client: MagicMock,
        mock_conversation: MagicMock,
    ) -> None:
        """Тест успешной обработки сообщения."""
        user_id, chat_id = 123, 456
        user_text = "Hello, bot!"
        expected_response = "Hi there! How can I help you?"

        mock_llm_client.get_response.return_value = expected_response

        response = await message_handler.handle_message(user_id, chat_id, user_text)

        # Проверяем что получили историю
        mock_conversation.get_history.assert_called_once_with(user_id, chat_id)

        # Проверяем что вызвали LLM с правильными сообщениями
        mock_llm_client.get_response.assert_called_once()
        call_args = mock_llm_client.get_response.call_args[0][0]
        assert call_args[-1]["role"] == "user"
        assert call_args[-1]["content"] == user_text

        # Проверяем что добавили сообщения в историю
        assert mock_conversation.add_message.call_count == 2
        # Первый вызов - сообщение пользователя
        mock_conversation.add_message.assert_any_call(user_id, chat_id, "user", user_text)
        # Второй вызов - ответ ассистента
        mock_conversation.add_message.assert_any_call(
            user_id, chat_id, "assistant", expected_response
        )

        # Проверяем возвращаемое значение
        assert response == expected_response

    async def test_handle_message_with_history(
        self,
        message_handler: MessageHandler,
        mock_llm_client: MagicMock,
        mock_conversation: MagicMock,
    ) -> None:
        """Тест обработки сообщения с существующей историей."""
        user_id, chat_id = 123, 456
        user_text = "What's the weather?"
        expected_response = "I don't have access to weather data."

        # Мокируем историю
        history: list[ChatMessage] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]
        mock_conversation.get_history.return_value = history
        mock_llm_client.get_response.return_value = expected_response

        response = await message_handler.handle_message(user_id, chat_id, user_text)

        # Проверяем что история была использована
        mock_llm_client.get_response.assert_called_once()
        call_args = mock_llm_client.get_response.call_args[0][0]

        # История + новое сообщение
        assert len(call_args) == 3
        assert call_args[0]["content"] == "Hello"
        assert call_args[1]["content"] == "Hi!"
        assert call_args[2]["content"] == user_text

        assert response == expected_response

    async def test_handle_message_empty_history(
        self,
        message_handler: MessageHandler,
        mock_llm_client: MagicMock,
        mock_conversation: MagicMock,
    ) -> None:
        """Тест обработки сообщения без истории."""
        user_id, chat_id = 789, 101
        user_text = "First message"
        expected_response = "Welcome!"

        mock_conversation.get_history.return_value = []
        mock_llm_client.get_response.return_value = expected_response

        response = await message_handler.handle_message(user_id, chat_id, user_text)

        # Проверяем что передали только одно сообщение
        call_args = mock_llm_client.get_response.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]["role"] == "user"
        assert call_args[0]["content"] == user_text

        assert response == expected_response

    async def test_handle_message_llm_error(
        self,
        message_handler: MessageHandler,
        mock_llm_client: MagicMock,
        mock_conversation: MagicMock,
    ) -> None:
        """Тест обработки ошибки от LLM."""
        user_id, chat_id = 123, 456
        user_text = "Test message"

        mock_llm_client.get_response.side_effect = Exception("LLM API error")

        with pytest.raises(Exception, match="LLM API error"):
            await message_handler.handle_message(user_id, chat_id, user_text)

        # Проверяем что история была запрошена
        mock_conversation.get_history.assert_called_once_with(user_id, chat_id)

        # Проверяем что сообщения НЕ были добавлены в историю при ошибке
        mock_conversation.add_message.assert_not_called()

    async def test_handle_message_different_users(
        self,
        message_handler: MessageHandler,
        mock_llm_client: MagicMock,
        mock_conversation: MagicMock,
    ) -> None:
        """Тест обработки сообщений от разных пользователей."""
        user1_id, chat1_id = 111, 222
        user2_id, chat2_id = 333, 444

        mock_llm_client.get_response.return_value = "Response"

        # Первое сообщение от пользователя 1
        await message_handler.handle_message(user1_id, chat1_id, "Message from user 1")

        # Второе сообщение от пользователя 2
        await message_handler.handle_message(user2_id, chat2_id, "Message from user 2")

        # Проверяем что история запрашивалась для каждого пользователя
        assert mock_conversation.get_history.call_count == 2
        mock_conversation.get_history.assert_any_call(user1_id, chat1_id)
        mock_conversation.get_history.assert_any_call(user2_id, chat2_id)

        # Проверяем что сообщения добавлялись для каждого пользователя
        assert mock_conversation.add_message.call_count == 4  # 2 пользователя * 2 сообщения
        mock_conversation.add_message.assert_any_call(
            user1_id, chat1_id, "user", "Message from user 1"
        )
        mock_conversation.add_message.assert_any_call(
            user2_id, chat2_id, "user", "Message from user 2"
        )

    def test_message_handler_initialization(self) -> None:
        """Тест инициализации MessageHandler."""
        mock_llm = MagicMock()
        mock_conv = MagicMock()

        handler = MessageHandler(llm_client=mock_llm, conversation=mock_conv)

        assert handler.llm_client == mock_llm
        assert handler.conversation == mock_conv
