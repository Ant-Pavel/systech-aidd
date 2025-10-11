import logging

from src.conversation import Conversation
from src.llm_client import LLMClient
from src.types import ChatMessage

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, llm_client: LLMClient, conversation: Conversation) -> None:
        self.llm_client: LLMClient = llm_client
        self.conversation: Conversation = conversation

    async def handle_message(self, user_id: int, chat_id: int, text: str) -> str:
        logger.info(f"Received message from user {user_id} in chat {chat_id}: {text}")

        # Получаем историю диалога
        history = self.conversation.get_history(user_id, chat_id)

        # Добавляем текущее сообщение пользователя
        messages = [*history, ChatMessage(role="user", content=text)]

        # Получаем ответ от LLM
        response = await self.llm_client.get_response(messages)

        # Сохраняем сообщение пользователя и ответ ассистента в историю
        self.conversation.add_message(user_id, chat_id, "user", text)
        self.conversation.add_message(user_id, chat_id, "assistant", response)

        logger.info(f"Response sent to user {user_id}")
        return response
