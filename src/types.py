"""Общие типы для проекта."""

from typing import TypedDict


class ChatMessage(TypedDict):
    """Структура сообщения для LLM API."""

    role: str
    content: str
