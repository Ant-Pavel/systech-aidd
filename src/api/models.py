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
