import logging
from pathlib import Path

from openai import APIError, APITimeoutError, AsyncOpenAI, AuthenticationError, RateLimitError

from src.types import ChatMessage

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        system_prompt_path: str | None = None,
    ) -> None:
        self.client: AsyncOpenAI = AsyncOpenAI(
            api_key=api_key, base_url="https://openrouter.ai/api/v1"
        )
        self.model: str = model
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        self.timeout: int = timeout
        self.system_prompt: str | None = None

        # Загрузка системного промпта из файла
        if system_prompt_path:
            self.system_prompt = self._load_system_prompt(system_prompt_path)

    def _load_system_prompt(self, prompt_path: str) -> str:
        """Загрузить системный промпт из файла."""
        path = Path(prompt_path)

        if not path.exists():
            msg = f"System prompt file not found: {prompt_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        prompt_content = path.read_text(encoding="utf-8").strip()

        if not prompt_content:
            msg = f"System prompt file is empty: {prompt_path}"
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"Loaded system prompt from {prompt_path}")
        return prompt_content

    async def get_response(self, messages: list[ChatMessage]) -> str:
        try:
            # Добавляем системный промпт в начало, если он определен
            final_messages = messages
            if self.system_prompt:
                system_message: ChatMessage = {"role": "system", "content": self.system_prompt}
                final_messages = [system_message, *messages]

            logger.info(f"Sending request to LLM with {len(final_messages)} messages")

            # OpenAI SDK ожидает специфичные типы, но наша структура ChatMessage совместима
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=final_messages,  # type: ignore[arg-type]
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
