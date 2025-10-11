"""Unit-тесты для модуля llm_client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import APIError, APITimeoutError, AuthenticationError, RateLimitError

from src.llm_client import LLMClient
from src.types import ChatMessage


class TestLLMClient:
    """Тесты для класса LLMClient."""

    @pytest.fixture
    def llm_client(self) -> LLMClient:
        """Фикстура для создания LLMClient."""
        return LLMClient(
            api_key="test_key",
            model="test_model",
            temperature=0.7,
            max_tokens=1000,
            timeout=30,
        )

    @pytest.fixture
    def sample_messages(self) -> list[ChatMessage]:
        """Фикстура с примерами сообщений."""
        return [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]

    async def test_get_response_success(
        self, llm_client: LLMClient, sample_messages: list[ChatMessage]
    ) -> None:
        """Тест успешного получения ответа от LLM."""
        expected_response = "I'm doing great, thanks for asking!"

        # Создаем мок для response
        mock_choice = MagicMock()
        mock_choice.message.content = expected_response

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        # Мокируем клиент
        with patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            response = await llm_client.get_response(sample_messages)

            assert response == expected_response
            mock_create.assert_called_once_with(
                model="test_model",
                messages=sample_messages,
                temperature=0.7,
                max_tokens=1000,
                timeout=30,
            )

    async def test_get_response_empty_content(
        self, llm_client: LLMClient, sample_messages: list[ChatMessage]
    ) -> None:
        """Тест обработки пустого ответа (None) от LLM."""
        mock_choice = MagicMock()
        mock_choice.message.content = None

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            with pytest.raises(Exception, match="Произошла непредвиденная ошибка"):
                await llm_client.get_response(sample_messages)

    async def test_get_response_timeout_error(
        self, llm_client: LLMClient, sample_messages: list[ChatMessage]
    ) -> None:
        """Тест обработки APITimeoutError."""
        with patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.side_effect = APITimeoutError(request=MagicMock())

            with pytest.raises(Exception, match="Timeout"):
                await llm_client.get_response(sample_messages)

    async def test_get_response_authentication_error(
        self, llm_client: LLMClient, sample_messages: list[ChatMessage]
    ) -> None:
        """Тест обработки AuthenticationError."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.side_effect = AuthenticationError(
                message="Invalid API key",
                response=mock_response,
                body=None,
            )

            with pytest.raises(Exception, match="Authentication error"):
                await llm_client.get_response(sample_messages)

    async def test_get_response_rate_limit_error(
        self, llm_client: LLMClient, sample_messages: list[ChatMessage]
    ) -> None:
        """Тест обработки RateLimitError."""
        mock_response = MagicMock()
        mock_response.status_code = 429

        with patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.side_effect = RateLimitError(
                message="Rate limit exceeded",
                response=mock_response,
                body=None,
            )

            with pytest.raises(Exception, match="Rate limit"):
                await llm_client.get_response(sample_messages)

    async def test_get_response_api_error(
        self, llm_client: LLMClient, sample_messages: list[ChatMessage]
    ) -> None:
        """Тест обработки общей APIError."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.side_effect = APIError(
                message="Internal server error",
                request=MagicMock(),
                body=None,
            )

            with pytest.raises(Exception, match="API error"):
                await llm_client.get_response(sample_messages)

    async def test_get_response_unexpected_error(
        self, llm_client: LLMClient, sample_messages: list[ChatMessage]
    ) -> None:
        """Тест обработки неожиданной ошибки."""
        with patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.side_effect = ValueError("Unexpected error")

            with pytest.raises(Exception, match="Произошла непредвиденная ошибка"):
                await llm_client.get_response(sample_messages)

    async def test_get_response_with_single_message(self, llm_client: LLMClient) -> None:
        """Тест с одним сообщением."""
        messages: list[ChatMessage] = [{"role": "user", "content": "Test"}]
        expected_response = "Test response"

        mock_choice = MagicMock()
        mock_choice.message.content = expected_response

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            response = await llm_client.get_response(messages)

            assert response == expected_response

    def test_llm_client_initialization(self) -> None:
        """Тест инициализации LLMClient."""
        client = LLMClient(
            api_key="my_key",
            model="gpt-4",
            temperature=0.5,
            max_tokens=2000,
            timeout=60,
        )

        assert client.model == "gpt-4"
        assert client.temperature == 0.5
        assert client.max_tokens == 2000
        assert client.timeout == 60
        assert client.client is not None
