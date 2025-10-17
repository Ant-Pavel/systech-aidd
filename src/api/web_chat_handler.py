"""Обработчик веб-чата с поддержкой стриминга LLM ответов."""

import logging
from collections.abc import AsyncGenerator

from src.database_conversation import DatabaseConversation
from src.protocols import LLMClientProtocol
from src.types import ChatMessage

logger = logging.getLogger(__name__)


class WebChatHandler:
    """Обработчик веб-чата с маппингом session_id на user_id и стримингом ответов."""

    def __init__(
        self,
        database_conversation: DatabaseConversation,
        llm_client: LLMClientProtocol,
        max_history_messages: int,
    ) -> None:
        """Инициализация обработчика веб-чата.

        Args:
            database_conversation: Хранилище диалогов
            llm_client: Клиент для работы с LLM
            max_history_messages: Максимальное количество сообщений в истории
        """
        self.db_conversation = database_conversation
        self.llm_client = llm_client
        self.max_history_messages = max_history_messages
        self.session_to_user_id: dict[str, int] = {}
        self.next_user_id = -1  # Отрицательные ID для веб-пользователей

    def get_or_create_user_id(self, session_id: str) -> int:
        """Получить или создать user_id для session_id.

        Args:
            session_id: ID сессии из localStorage

        Returns:
            int: user_id (отрицательный для веб-пользователей)
        """
        if session_id not in self.session_to_user_id:
            self.session_to_user_id[session_id] = self.next_user_id
            logger.info(f"Created new web user_id {self.next_user_id} for session {session_id}")
            self.next_user_id -= 1
        return self.session_to_user_id[session_id]

    async def handle_message_stream(
        self, session_id: str, message: str
    ) -> AsyncGenerator[str, None]:
        """Обработать сообщение пользователя со стримингом ответа.

        Алгоритм:
        1. Получить user_id для session_id
        2. Сохранить сообщение пользователя в БД (source='web')
        3. Получить историю диалога
        4. Стримить ответ от LLM (yield chunks)
        5. После завершения стрима сохранить полный ответ в БД

        Args:
            session_id: ID сессии пользователя
            message: Текст сообщения пользователя

        Yields:
            str: Chunks текста ответа от LLM

        Raises:
            Exception: При ошибках работы с БД или LLM
        """
        user_id = self.get_or_create_user_id(session_id)
        chat_id = user_id  # Для веб chat_id = user_id

        logger.info(
            f"Handling web chat message from user {user_id} (session {session_id}): {message[:50]}..."
        )

        # Сохранить сообщение пользователя
        await self.db_conversation.add_message(
            user_id, chat_id, "user", message, source="web"
        )

        # Получить историю диалога
        history = await self.db_conversation.get_history(user_id, chat_id)

        # Добавить текущее сообщение пользователя в контекст
        # История уже содержит текущее сообщение, т.к. мы его только что сохранили
        # Но для LLM нужно передать список ChatMessage
        messages: list[ChatMessage] = [
            {"role": msg["role"], "content": msg["content"]} for msg in history
        ]

        # Стримить ответ от LLM и накапливать полный ответ
        full_response = ""
        try:
            async for chunk in self.llm_client.get_response_stream(messages):
                full_response += chunk
                yield chunk

            # Сохранить полный ответ ассистента в БД
            await self.db_conversation.add_message(
                user_id, chat_id, "assistant", full_response, source="web"
            )

            logger.info(
                f"Web chat response completed for user {user_id}, "
                f"response length: {len(full_response)}"
            )

        except Exception as e:
            logger.error(f"Error in web chat message streaming: {e}", exc_info=True)
            raise

    async def get_history(self, session_id: str) -> list[ChatMessage]:
        """Получить историю диалога для session_id.

        Args:
            session_id: ID сессии пользователя

        Returns:
            list[ChatMessage]: Список сообщений из истории
        """
        user_id = self.get_or_create_user_id(session_id)
        chat_id = user_id

        logger.info(f"Retrieving web chat history for user {user_id} (session {session_id})")

        history = await self.db_conversation.get_history(user_id, chat_id)

        # Преобразуем в формат ChatMessage
        return [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                created_at=msg.get("created_at", ""),
                message_length=msg.get("message_length", 0),
            )
            for msg in history
        ]

