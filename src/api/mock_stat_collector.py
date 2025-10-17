"""Mock реализация сборщика статистики для разработки и тестирования."""

import math
import random
from datetime import datetime, timedelta
from typing import Literal

from src.api.models import DashboardStats, MetricCard, MetricsData, TimeSeriesPoint


class MockStatCollector:
    """Mock реализация StatCollectorProtocol.

    Генерирует реалистичные тестовые данные для дашборда.
    Используется для разработки frontend без подключения к реальной БД.
    """

    def __init__(self, seed: int | None = None) -> None:
        """Инициализация Mock сборщика.

        Args:
            seed: Seed для генератора случайных чисел (для детерминированных тестов)
        """
        if seed is not None:
            random.seed(seed)

    async def get_dashboard_stats(self, period: str) -> DashboardStats:
        """Получить mock статистику для дашборда за указанный период.

        Args:
            period: Период для статистики ('7d', '30d', '3m')

        Returns:
            DashboardStats: Сгенерированная статистика

        Raises:
            ValueError: Если period имеет невалидное значение
        """
        if period not in ["7d", "30d", "3m"]:
            raise ValueError(f"Invalid period: {period}. Must be one of: 7d, 30d, 3m")

        # Генерируем базовые метрики
        metrics = self._generate_metrics(period)

        # Генерируем временной ряд
        time_series = self._generate_time_series(period)

        return DashboardStats(metrics=metrics, time_series=time_series)

    def _generate_metrics(self, period: str) -> MetricsData:
        """Генерация метрик для дашборда.

        Args:
            period: Период для статистики

        Returns:
            MetricsData: Сгенерированные метрики
        """
        # Базовые значения зависят от периода
        base_multiplier = {"7d": 1.0, "30d": 4.0, "3m": 12.0}[period]

        # Общее количество сообщений
        total_messages_value = int(3000 * base_multiplier + random.randint(-500, 500))
        total_messages = self._create_metric_card(
            value=total_messages_value,
            base_change=random.uniform(-20, 25),
            description_templates={
                "up": "Trending up this month",
                "down": "Acquisition needs attention",
                "stable": "Stable performance",
            },
        )

        # Активные диалоги
        active_conversations_value = int(250 * base_multiplier + random.randint(-50, 50))
        active_conversations = self._create_metric_card(
            value=active_conversations_value,
            base_change=random.uniform(-15, 20),
            description_templates={
                "up": "Strong user retention",
                "down": "Down this period",
                "stable": "Engagement stable",
            },
        )

        # Средняя длина диалога
        avg_length_value = round(
            total_messages_value / active_conversations_value
            if active_conversations_value > 0
            else 0,
            1,
        )
        avg_conversation_length = self._create_metric_card(
            value=avg_length_value,
            base_change=random.uniform(-10, 15),
            description_templates={
                "up": "Steady performance increase",
                "down": "Shorter conversations",
                "stable": "Meets growth projections",
            },
        )

        return MetricsData(
            total_messages=total_messages,
            active_conversations=active_conversations,
            avg_conversation_length=avg_conversation_length,
        )

    def _create_metric_card(
        self,
        value: float,
        base_change: float,
        description_templates: dict[str, str],
    ) -> MetricCard:
        """Создать карточку метрики с расчетом тренда.

        Args:
            value: Значение метрики
            base_change: Базовое процентное изменение
            description_templates: Шаблоны описаний для разных трендов

        Returns:
            MetricCard: Карточка метрики с трендом
        """
        change_percent = round(base_change, 1)

        # Определяем тренд
        trend: Literal["up", "down", "stable"]
        if change_percent > 2:
            trend = "up"
        elif change_percent < -2:
            trend = "down"
        else:
            trend = "stable"

        description = description_templates[trend]

        return MetricCard(
            value=value,
            change_percent=change_percent,
            trend=trend,
            description=description,
        )

    def _generate_time_series(self, period: str) -> list[TimeSeriesPoint]:
        """Генерация временного ряда для графика.

        Args:
            period: Период для статистики

        Returns:
            list[TimeSeriesPoint]: Список точек временного ряда
        """
        today = datetime.now().date()

        # Параметры генерации зависят от периода
        if period == "7d":
            days = 7
            base_value = 400
            variation = 100
        elif period == "30d":
            days = 30
            base_value = 420
            variation = 120
        else:  # 3m
            days = 90
            base_value = 450
            variation = 150

        time_series: list[TimeSeriesPoint] = []

        # Генерируем данные с реалистичными колебаниями
        for i in range(days):
            date = today - timedelta(days=days - 1 - i)

            # Добавляем тренд и случайные колебания
            trend_component = i * 2  # Небольшой восходящий тренд
            random_component = random.randint(-variation, variation)
            weekly_pattern = int(50 * math.sin(i * 3.14 / 3.5))  # Недельная цикличность

            value = max(
                0,
                base_value + trend_component + random_component + weekly_pattern,
            )

            time_series.append(
                TimeSeriesPoint(
                    date=date.isoformat(),
                    value=value,
                )
            )

        return time_series
