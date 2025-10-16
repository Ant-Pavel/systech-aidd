"""Управление историей диалогов в памяти."""

import logging

from src.types import ChatMessage

logger = logging.getLogger(__name__)


class Conversation:
    def __init__(self, max_history_messages: int) -> None:
        self.conversations: dict[tuple[int, int], list[ChatMessage]] = {}
        self.max_history_messages: int = max_history_messages

    def add_message(self, user_id: int, chat_id: int, role: str, content: str) -> None:
        key = (user_id, chat_id)

        if key not in self.conversations:
            self.conversations[key] = []

        # Добавляем новое сообщение
        self.conversations[key].append(ChatMessage(role=role, content=content))

        # Ограничиваем историю максимальным количеством сообщений
        if len(self.conversations[key]) > self.max_history_messages:
            self.conversations[key] = self.conversations[key][-self.max_history_messages :]

        logger.info(
            f"Message added to history for user {user_id}, chat {chat_id}. "
            f"Total messages: {len(self.conversations[key])}"
        )

    def get_history(self, user_id: int, chat_id: int) -> list[ChatMessage]:
        key = (user_id, chat_id)
        history = self.conversations.get(key, [])
        logger.info(f"Retrieved {len(history)} messages for user {user_id}, chat {chat_id}")
        return history

    def clear_history(self, user_id: int, chat_id: int) -> None:
        key = (user_id, chat_id)
        if key in self.conversations:
            del self.conversations[key]
            logger.info(f"History cleared for user {user_id}, chat {chat_id}")
        else:
            logger.info(f"No history to clear for user {user_id}, chat {chat_id}")
