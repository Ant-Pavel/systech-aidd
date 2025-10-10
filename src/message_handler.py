import logging

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def handle_message(self, user_id, chat_id, text):
        logger.info(f"Received message from user {user_id} in chat {chat_id}: {text}")
        
        # Формируем простой запрос (без истории на этой итерации)
        messages = [
            {"role": "user", "content": text}
        ]
        
        # Получаем ответ от LLM
        response = await self.llm_client.get_response(messages)
        
        logger.info(f"Response sent to user {user_id}")
        return response

