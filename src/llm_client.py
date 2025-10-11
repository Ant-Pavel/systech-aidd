import logging

from openai import APIError, APITimeoutError, AsyncOpenAI, AuthenticationError, RateLimitError

from src.types import ChatMessage

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(
        self, api_key: str, model: str, temperature: float, max_tokens: int, timeout: int
    ) -> None:
        self.client: AsyncOpenAI = AsyncOpenAI(
            api_key=api_key, base_url="https://openrouter.ai/api/v1"
        )
        self.model: str = model
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        self.timeout: int = timeout

    async def get_response(self, messages: list[ChatMessage]) -> str:
        try:
            logger.info(f"Sending request to LLM with {len(messages)} messages")

            # OpenAI SDK ожидает специфичные типы, но наша структура ChatMessage совместима
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )

            answer = response.choices[0].message.content
            if answer is None:
                raise Exception("LLM returned empty response")

            logger.info(f"Received response: {answer[:100]}...")
            return answer

        except APITimeoutError as e:
            logger.error(f"LLM API timeout error: {e}", exc_info=True)
            msg = "Timeout: Запрос к LLM превысил лимит времени. Попробуйте еще раз."
            raise Exception(msg) from e

        except AuthenticationError as e:
            logger.error(f"LLM API authentication error: {e}", exc_info=True)
            raise Exception("Authentication error: Проверьте API ключ Openrouter.") from e

        except RateLimitError as e:
            logger.error(f"LLM API rate limit error: {e}", exc_info=True)
            raise Exception("Rate limit: Превышен лимит запросов. Попробуйте позже.") from e

        except APIError as e:
            logger.error(f"LLM API error: {e}", exc_info=True)
            raise Exception(f"API error: {e!s}") from e

        except Exception as e:
            logger.error(f"Unexpected error in LLM client: {e}", exc_info=True)
            raise Exception("Произошла непредвиденная ошибка. Попробуйте еще раз.") from e
