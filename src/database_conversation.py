"""Управление историей диалогов в PostgreSQL через asyncpg."""

import logging
from datetime import datetime

from src.database import get_pool
from src.types import ChatMessage

logger = logging.getLogger(__name__)


class DatabaseConversation:
    """Управление историей диалогов в PostgreSQL с поддержкой soft delete."""

    def __init__(self, max_history_messages: int) -> None:
        """Инициализация хранилища диалогов.

        Args:
            max_history_messages: Максимальное количество сообщений в истории
        """
        self.max_history_messages = max_history_messages

    async def add_message(
        self, user_id: int, chat_id: int, role: str, content: str, source: str = "telegram"
    ) -> None:
        """Добавить сообщение в историю диалога.

        Args:
            user_id: ID пользователя Telegram
            chat_id: ID чата Telegram
            role: Роль отправителя ('user' или 'assistant')
            content: Текст сообщения
            source: Источник сообщения ('telegram' или 'web')
        """
        pool = await get_pool()
        message_length = len(content)

        async with pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO messages (user_id, chat_id, role, content, message_length, source)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                user_id,
                chat_id,
                role,
                content,
                message_length,
                source,
            )

        logger.info(
            f"Message added to database for user {user_id}, chat {chat_id}, "
            f"role={role}, length={message_length}"
        )

    async def get_history(self, user_id: int, chat_id: int) -> list[ChatMessage]:
        """Получить историю диалога для пользователя и чата.

        Возвращает только не удаленные сообщения (soft delete).

        Args:
            user_id: ID пользователя Telegram
            chat_id: ID чата Telegram

        Returns:
            list[ChatMessage]: Список последних N сообщений
        """
        pool = await get_pool()

        async with pool.acquire() as connection:
            rows = await connection.fetch(
                """
                SELECT role, content, created_at, message_length
                FROM messages
                WHERE user_id = $1 AND chat_id = $2 AND deleted_at IS NULL
                ORDER BY created_at DESC
                LIMIT $3
                """,
                user_id,
                chat_id,
                self.max_history_messages,
            )

        # Преобразуем записи в ChatMessage и разворачиваем (т.к. выбрали DESC)
        messages: list[ChatMessage] = []
        for row in reversed(rows):
            messages.append(
                ChatMessage(
                    role=row["role"],
                    content=row["content"],
                    created_at=row["created_at"].isoformat(),
                    message_length=row["message_length"],
                )
            )

        logger.info(f"Retrieved {len(messages)} messages for user {user_id}, chat {chat_id}")
        return messages

    async def clear_history(self, user_id: int, chat_id: int) -> None:
        """Очистить историю диалога (soft delete).

        Устанавливает deleted_at для всех сообщений пользователя в чате.

        Args:
            user_id: ID пользователя Telegram
            chat_id: ID чата Telegram
        """
        pool = await get_pool()

        async with pool.acquire() as connection:
            result = await connection.execute(
                """
                UPDATE messages
                SET deleted_at = $1
                WHERE user_id = $2 AND chat_id = $3 AND deleted_at IS NULL
                """,
                datetime.now(),
                user_id,
                chat_id,
            )

        # result имеет формат "UPDATE N" где N - количество обновленных строк
        rows_affected = int(result.split()[-1]) if result else 0

        if rows_affected > 0:
            logger.info(
                f"History soft-deleted for user {user_id}, chat {chat_id}. "
                f"Affected rows: {rows_affected}"
            )
        else:
            logger.info(f"No history to clear for user {user_id}, chat {chat_id}")

