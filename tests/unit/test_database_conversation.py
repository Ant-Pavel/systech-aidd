"""Unit-тесты для модуля database_conversation."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.database_conversation import DatabaseConversation


class TestDatabaseConversation:
    """Тесты для класса DatabaseConversation."""

    @pytest.fixture
    def db_conversation(self) -> DatabaseConversation:
        """Создать экземпляр DatabaseConversation для тестов."""
        return DatabaseConversation(max_history_messages=10)

    @pytest.mark.asyncio
    async def test_add_message_success(self, db_conversation: DatabaseConversation) -> None:
        """Тест успешного добавления сообщения в БД."""
        mock_connection = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_connection), __aexit__=AsyncMock()
            )
        )

        with patch(
            "src.database_conversation.get_pool", new_callable=AsyncMock, return_value=mock_pool
        ):
            await db_conversation.add_message(
                user_id=12345,
                chat_id=67890,
                role="user",
                content="Hello, world!",
            )

        # Проверяем, что execute был вызван с правильными параметрами
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        assert "INSERT INTO messages" in call_args[0][0]
        assert call_args[0][1] == 12345  # user_id
        assert call_args[0][2] == 67890  # chat_id
        assert call_args[0][3] == "user"  # role
        assert call_args[0][4] == "Hello, world!"  # content
        assert call_args[0][5] == 13  # message_length

    @pytest.mark.asyncio
    async def test_get_history_with_messages(self, db_conversation: DatabaseConversation) -> None:
        """Тест получения истории с сообщениями из БД."""
        mock_connection = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_connection), __aexit__=AsyncMock()
            )
        )

        # Мокаем результат из БД (ORDER BY created_at DESC)
        mock_rows = [
            {
                "role": "assistant",
                "content": "Hi there!",
                "created_at": datetime(2025, 10, 16, 12, 0, 1),
                "message_length": 9,
            },
            {
                "role": "user",
                "content": "Hello",
                "created_at": datetime(2025, 10, 16, 12, 0, 0),
                "message_length": 5,
            },
        ]
        mock_connection.fetch.return_value = mock_rows

        with patch(
            "src.database_conversation.get_pool", new_callable=AsyncMock, return_value=mock_pool
        ):
            history = await db_conversation.get_history(user_id=123, chat_id=456)

        # Проверяем SQL запрос
        mock_connection.fetch.assert_called_once()
        call_args = mock_connection.fetch.call_args
        assert "SELECT role, content, created_at, message_length" in call_args[0][0]
        assert "WHERE user_id = $1 AND chat_id = $2 AND deleted_at IS NULL" in call_args[0][0]
        assert "ORDER BY created_at DESC" in call_args[0][0]
        assert "LIMIT $3" in call_args[0][0]

        # Проверяем результат (должен быть развернут, т.к. выбрали DESC)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[0]["created_at"] == "2025-10-16T12:00:00"
        assert history[0]["message_length"] == 5
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"

    @pytest.mark.asyncio
    async def test_get_history_empty(self, db_conversation: DatabaseConversation) -> None:
        """Тест получения пустой истории."""
        mock_connection = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_connection), __aexit__=AsyncMock()
            )
        )
        mock_connection.fetch.return_value = []

        with patch(
            "src.database_conversation.get_pool", new_callable=AsyncMock, return_value=mock_pool
        ):
            history = await db_conversation.get_history(user_id=123, chat_id=456)

        assert history == []

    @pytest.mark.asyncio
    async def test_clear_history_soft_delete(self, db_conversation: DatabaseConversation) -> None:
        """Тест soft delete истории (UPDATE deleted_at)."""
        mock_connection = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_connection), __aexit__=AsyncMock()
            )
        )
        mock_connection.execute.return_value = "UPDATE 5"  # 5 строк обновлено

        with patch(
            "src.database_conversation.get_pool", new_callable=AsyncMock, return_value=mock_pool
        ):
            await db_conversation.clear_history(user_id=123, chat_id=456)

        # Проверяем SQL запрос
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        assert "UPDATE messages" in call_args[0][0]
        assert "SET deleted_at = $1" in call_args[0][0]
        assert "WHERE user_id = $2 AND chat_id = $3 AND deleted_at IS NULL" in call_args[0][0]
        assert isinstance(call_args[0][1], datetime)  # deleted_at timestamp
        assert call_args[0][2] == 123  # user_id
        assert call_args[0][3] == 456  # chat_id

    @pytest.mark.asyncio
    async def test_clear_history_no_rows(self, db_conversation: DatabaseConversation) -> None:
        """Тест очистки истории когда нет сообщений."""
        mock_connection = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_connection), __aexit__=AsyncMock()
            )
        )
        mock_connection.execute.return_value = "UPDATE 0"  # 0 строк обновлено

        with patch(
            "src.database_conversation.get_pool", new_callable=AsyncMock, return_value=mock_pool
        ):
            await db_conversation.clear_history(user_id=123, chat_id=456)

        # Должно выполниться без ошибок
        mock_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_max_history_limit(self, db_conversation: DatabaseConversation) -> None:
        """Тест что get_history учитывает лимит сообщений."""
        mock_connection = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_connection), __aexit__=AsyncMock()
            )
        )
        mock_connection.fetch.return_value = []

        with patch(
            "src.database_conversation.get_pool", new_callable=AsyncMock, return_value=mock_pool
        ):
            await db_conversation.get_history(user_id=123, chat_id=456)

        # Проверяем что лимит передается в SQL
        call_args = mock_connection.fetch.call_args
        assert call_args[0][3] == 10  # max_history_messages

    @pytest.mark.asyncio
    async def test_message_length_calculation(self, db_conversation: DatabaseConversation) -> None:
        """Тест что message_length правильно вычисляется."""
        mock_connection = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_connection), __aexit__=AsyncMock()
            )
        )

        content = "Тест с кириллицей и эмодзи 😀"

        with patch(
            "src.database_conversation.get_pool", new_callable=AsyncMock, return_value=mock_pool
        ):
            await db_conversation.add_message(
                user_id=123,
                chat_id=456,
                role="user",
                content=content,
            )

        call_args = mock_connection.execute.call_args
        assert call_args[0][5] == len(content)  # message_length должна быть длина строки

    @pytest.mark.asyncio
    async def test_database_conversation_initialization(self) -> None:
        """Тест инициализации DatabaseConversation."""
        conv = DatabaseConversation(max_history_messages=20)
        assert conv.max_history_messages == 20

    @pytest.mark.asyncio
    async def test_get_history_returns_chat_message_type(
        self, db_conversation: DatabaseConversation
    ) -> None:
        """Тест что get_history возвращает правильный тип ChatMessage."""
        mock_connection = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_connection), __aexit__=AsyncMock()
            )
        )

        mock_rows = [
            {
                "role": "user",
                "content": "Test",
                "created_at": datetime(2025, 10, 16, 12, 0, 0),
                "message_length": 4,
            }
        ]
        mock_connection.fetch.return_value = mock_rows

        with patch(
            "src.database_conversation.get_pool", new_callable=AsyncMock, return_value=mock_pool
        ):
            history = await db_conversation.get_history(user_id=123, chat_id=456)

        assert len(history) == 1
        message = history[0]
        # Проверяем что все ключи ChatMessage присутствуют
        assert "role" in message
        assert "content" in message
        assert "created_at" in message
        assert "message_length" in message
