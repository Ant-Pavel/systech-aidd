"""Реальная реализация сборщика статистики на основе БД."""

import logging
from datetime import datetime, timedelta
from typing import Literal

from src.api.models import DashboardStats, MetricCard, MetricsData, TimeSeriesPoint
from src.database import get_pool

logger = logging.getLogger(__name__)


class RealStatCollector:
    """Реальная реализация StatCollectorProtocol.

    Получает статистику из БД PostgreSQL.
    Учитывает сообщения из всех источников (Telegram и Web).
    """

    async def get_dashboard_stats(self, period: str) -> DashboardStats:
        """Получить статистику для дашборда за указанный период.

        Args:
            period: Период для статистики ('7d', '30d', '3m')

        Returns:
            DashboardStats: Статистика из БД

        Raises:
            ValueError: Если period имеет невалидное значение
        """
        if period not in ["7d", "30d", "3m"]:
            raise ValueError(f"Invalid period: {period}. Must be one of: 7d, 30d, 3m")

        logger.info(f"Collecting dashboard stats for period: {period} (all sources)")

        # Вычисляем даты для текущего и предыдущего периодов
        period_days = {"7d": 7, "30d": 30, "3m": 90}[period]
        current_period_start = datetime.now() - timedelta(days=period_days)
        previous_period_start = current_period_start - timedelta(days=period_days)

        # Получаем метрики
        metrics = await self._get_metrics(
            current_period_start, previous_period_start, period_days
        )

        # Получаем временной ряд
        time_series = await self._get_time_series(current_period_start, period_days)

        return DashboardStats(metrics=metrics, time_series=time_series)

    async def _get_metrics(
        self,
        current_period_start: datetime,
        previous_period_start: datetime,
        period_days: int,
    ) -> MetricsData:
        """Получить метрики из БД.

        Args:
            current_period_start: Начало текущего периода
            previous_period_start: Начало предыдущего периода
            period_days: Количество дней в периоде

        Returns:
            MetricsData: Метрики для дашборда
        """
        pool = await get_pool()

        async with pool.acquire() as connection:
            # Запрос для текущего периода (все источники: telegram и web)
            current_stats = await connection.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT CONCAT(user_id::text, '_', chat_id::text)) as active_conversations
                FROM messages
                WHERE deleted_at IS NULL
                    AND created_at >= $1
                """,
                current_period_start,
            )

            # Запрос для предыдущего периода (для расчета изменений)
            previous_stats = await connection.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT CONCAT(user_id::text, '_', chat_id::text)) as active_conversations
                FROM messages
                WHERE deleted_at IS NULL
                    AND created_at >= $1 AND created_at < $2
                """,
                previous_period_start,
                current_period_start,
            )

        # Извлекаем значения
        current_total = current_stats["total_messages"] if current_stats else 0
        previous_total = previous_stats["total_messages"] if previous_stats else 0

        current_conversations = current_stats["active_conversations"] if current_stats else 0
        previous_conversations = (
            previous_stats["active_conversations"] if previous_stats else 0
        )

        # Вычисляем средние длины диалогов
        current_avg_length = (
            round(current_total / current_conversations, 1) if current_conversations > 0 else 0
        )
        previous_avg_length = (
            round(previous_total / previous_conversations, 1)
            if previous_conversations > 0
            else 0
        )

        # Создаем карточки метрик с расчетом изменений
        total_messages_card = self._create_metric_card(
            value=current_total,
            previous_value=previous_total,
            description_templates={
                "up": "Trending up this period",
                "down": "Messages decreased",
                "stable": "Stable message volume",
            },
        )

        active_conversations_card = self._create_metric_card(
            value=current_conversations,
            previous_value=previous_conversations,
            description_templates={
                "up": "Strong user engagement",
                "down": "Fewer active conversations",
                "stable": "Stable conversation count",
            },
        )

        avg_conversation_length_card = self._create_metric_card(
            value=current_avg_length,
            previous_value=previous_avg_length,
            description_templates={
                "up": "Longer conversations",
                "down": "Shorter conversations",
                "stable": "Consistent conversation length",
            },
        )

        return MetricsData(
            total_messages=total_messages_card,
            active_conversations=active_conversations_card,
            avg_conversation_length=avg_conversation_length_card,
        )

    def _create_metric_card(
        self,
        value: float,
        previous_value: float,
        description_templates: dict[str, str],
    ) -> MetricCard:
        """Создать карточку метрики с расчетом тренда.

        Args:
            value: Текущее значение метрики
            previous_value: Значение метрики в предыдущем периоде
            description_templates: Шаблоны описаний для разных трендов

        Returns:
            MetricCard: Карточка метрики с трендом
        """
        # Рассчитываем процентное изменение
        if previous_value > 0:
            change_percent = round(((value - previous_value) / previous_value) * 100, 1)
        elif value > 0:
            change_percent = 100.0  # Рост с нуля
        else:
            change_percent = 0.0  # Оба значения нулевые

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

    async def _get_time_series(
        self, period_start: datetime, period_days: int
    ) -> list[TimeSeriesPoint]:
        """Получить временной ряд для графика.

        Args:
            period_start: Начало периода
            period_days: Количество дней в периоде

        Returns:
            list[TimeSeriesPoint]: Список точек временного ряда
        """
        pool = await get_pool()

        async with pool.acquire() as connection:
            # Группируем сообщения по дням (все источники: telegram и web)
            rows = await connection.fetch(
                """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as message_count
                FROM messages
                WHERE deleted_at IS NULL
                    AND created_at >= $1
                GROUP BY DATE(created_at)
                ORDER BY date ASC
                """,
                period_start,
            )

        # Создаем словарь дата -> количество сообщений
        date_to_count = {row["date"]: row["message_count"] for row in rows}

        # Генерируем полный временной ряд (включая дни с нулевыми значениями)
        time_series: list[TimeSeriesPoint] = []
        current_date = period_start.date()
        end_date = datetime.now().date()

        while current_date <= end_date:
            value = date_to_count.get(current_date, 0)
            time_series.append(
                TimeSeriesPoint(
                    date=current_date.isoformat(),
                    value=value,
                )
            )
            current_date += timedelta(days=1)

        logger.info(f"Generated time series with {len(time_series)} points")

        return time_series

