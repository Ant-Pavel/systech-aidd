"""Protocol интерфейсы для API модуля."""

from typing import Protocol

from src.api.models import DashboardStats


class StatCollectorProtocol(Protocol):
    """Protocol для сборщика статистики дашборда.

    Определяет интерфейс для получения статистики за различные периоды.
    Может иметь разные реализации: Mock (тестовые данные) и Real (из БД).
    """

    async def get_dashboard_stats(self, period: str) -> DashboardStats:
        """Получить статистику для дашборда за указанный период.

        Args:
            period: Период для статистики ('7d', '30d', '3m')

        Returns:
            DashboardStats: Полная статистика включая метрики и временной ряд

        Raises:
            ValueError: Если period имеет невалидное значение
        """
        ...
