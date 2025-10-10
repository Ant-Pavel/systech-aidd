import logging
from openai import AsyncOpenAI, APIError, APITimeoutError, AuthenticationError, RateLimitError

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
            
        except APITimeoutError as e:
            logger.error(f"LLM API timeout error: {e}", exc_info=True)
            raise Exception("Timeout: Запрос к LLM превысил лимит времени. Попробуйте еще раз.")
        
        except AuthenticationError as e:
            logger.error(f"LLM API authentication error: {e}", exc_info=True)
            raise Exception("Authentication error: Проверьте API ключ Openrouter.")
        
        except RateLimitError as e:
            logger.error(f"LLM API rate limit error: {e}", exc_info=True)
            raise Exception("Rate limit: Превышен лимит запросов. Попробуйте позже.")
        
        except APIError as e:
            logger.error(f"LLM API error: {e}", exc_info=True)
            raise Exception(f"API error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error in LLM client: {e}", exc_info=True)
            raise Exception("Произошла непредвиденная ошибка. Попробуйте еще раз.")

