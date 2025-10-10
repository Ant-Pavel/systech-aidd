import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, api_key, model, temperature, max_tokens, timeout):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
    
    async def get_response(self, messages):
        try:
            logger.info(f"Sending request to LLM with {len(messages)} messages")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Received response: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"LLM API error: {e}", exc_info=True)
            raise

