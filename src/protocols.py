"""Protocol интерфейсы для зависимостей."""

from typing import Protocol

from src.types import ChatMessage


class ConversationStorageProtocol(Protocol):
    """Protocol для работы с историей диалогов."""

    def add_message(self, user_id: int, chat_id: int, role: str, content: str) -> None:
        """Добавить сообщение в историю диалога."""
        ...

    def get_history(self, user_id: int, chat_id: int) -> list[ChatMessage]:
        """Получить историю диалога для пользователя и чата."""
        ...

    def clear_history(self, user_id: int, chat_id: int) -> None:
        """Очистить историю диалога для пользователя и чата."""
        ...


class LLMClientProtocol(Protocol):
    """Protocol для работы с LLM."""

    async def get_response(self, messages: list[ChatMessage]) -> str:
        """Получить ответ от LLM на основе истории сообщений."""
        ...
