"""Общие типы для проекта."""

from typing import NotRequired, TypedDict


class ChatMessage(TypedDict):
    """Структура сообщения для LLM API.

    Поля created_at и message_length опциональные - они используются
    для хранения в БД, но не требуются для LLM API.
    """

    role: str
    content: str
    created_at: NotRequired[str]  # ISO 8601 формат (YYYY-MM-DDTHH:MM:SS)
    message_length: NotRequired[int]  # Длина сообщения в символах
