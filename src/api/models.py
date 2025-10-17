"""Pydantic модели для API responses."""

from typing import Literal

from pydantic import BaseModel, Field


class MetricCard(BaseModel):
    """Данные для одной карточки метрики на дашборде.

    Attributes:
        value: Значение метрики (целое или дробное число)
        change_percent: Процентное изменение относительно предыдущего периода
        trend: Направление тренда (up/down/stable)
        description: Текстовое описание тренда для пользователя
    """

    value: float = Field(..., description="Значение метрики")
    change_percent: float = Field(
        ..., description="Процентное изменение относительно предыдущего периода"
    )
    trend: Literal["up", "down", "stable"] = Field(..., description="Направление тренда")
    description: str = Field(..., description="Текстовое описание тренда")


class TimeSeriesPoint(BaseModel):
    """Точка данных на временном графике.

    Attributes:
        date: Дата в формате ISO 8601 (YYYY-MM-DD)
        value: Количество сообщений на эту дату
    """

    date: str = Field(..., description="Дата в формате ISO 8601 (YYYY-MM-DD)")
    value: int = Field(..., ge=0, description="Количество сообщений")


class MetricsData(BaseModel):
    """Коллекция всех метрик дашборда.

    Attributes:
        total_messages: Общее количество сообщений
        active_conversations: Количество активных диалогов
        avg_conversation_length: Средняя длина диалога
    """

    total_messages: MetricCard = Field(..., description="Общее количество сообщений")
    active_conversations: MetricCard = Field(..., description="Количество активных диалогов")
    avg_conversation_length: MetricCard = Field(..., description="Средняя длина диалога")


class DashboardStats(BaseModel):
    """Полная статистика для дашборда.

    Attributes:
        metrics: Коллекция метрик (карточки)
        time_series: Данные временного ряда для графика
    """

    metrics: MetricsData = Field(..., description="Метрики дашборда")
    time_series: list[TimeSeriesPoint] = Field(
        ..., description="Временной ряд для графика", min_length=1
    )


# ===== Модели для веб-чата =====


class ChatRequest(BaseModel):
    """Запрос на отправку сообщения в чат.

    Attributes:
        session_id: Уникальный ID сессии пользователя (из localStorage)
        message: Текст сообщения пользователя
    """

    session_id: str = Field(..., description="ID сессии пользователя", min_length=1)
    message: str = Field(..., description="Текст сообщения", min_length=1)


class ChatMessageResponse(BaseModel):
    """Сообщение из истории чата.

    Attributes:
        role: Роль отправителя ('user' или 'assistant')
        content: Текст сообщения
        created_at: Время создания сообщения (ISO format)
    """

    role: str = Field(..., description="Роль отправителя")
    content: str = Field(..., description="Текст сообщения")
    created_at: str = Field(..., description="Время создания (ISO format)")


class StreamEvent(BaseModel):
    """Событие стрима SSE.

    Attributes:
        type: Тип события ('token', 'done', 'error')
        content: Содержимое события (chunk текста или сообщение об ошибке)
    """

    type: Literal["token", "done", "error"] = Field(..., description="Тип события")
    content: str = Field(..., description="Содержимое события")