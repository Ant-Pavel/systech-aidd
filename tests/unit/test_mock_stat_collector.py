"""Unit тесты для MockStatCollector."""

import pytest

from src.api.mock_stat_collector import MockStatCollector
from src.api.models import DashboardStats


class TestMockStatCollector:
    """Тесты для MockStatCollector."""

    @pytest.fixture
    def collector(self) -> MockStatCollector:
        """Фикстура для создания MockStatCollector с фиксированным seed."""
        return MockStatCollector(seed=42)

    async def test_get_dashboard_stats_7d(self, collector: MockStatCollector) -> None:
        """Тест получения статистики за 7 дней."""
        stats = await collector.get_dashboard_stats("7d")

        assert isinstance(stats, DashboardStats)
        assert stats.metrics.total_messages.value > 0
        assert stats.metrics.active_conversations.value > 0
        assert stats.metrics.avg_conversation_length.value > 0
        assert len(stats.time_series) == 7

    async def test_get_dashboard_stats_30d(self, collector: MockStatCollector) -> None:
        """Тест получения статистики за 30 дней."""
        stats = await collector.get_dashboard_stats("30d")

        assert isinstance(stats, DashboardStats)
        assert stats.metrics.total_messages.value > 0
        assert len(stats.time_series) == 30

    async def test_get_dashboard_stats_3m(self, collector: MockStatCollector) -> None:
        """Тест получения статистики за 3 месяца."""
        stats = await collector.get_dashboard_stats("3m")

        assert isinstance(stats, DashboardStats)
        assert stats.metrics.total_messages.value > 0
        assert len(stats.time_series) == 90

    async def test_invalid_period(self, collector: MockStatCollector) -> None:
        """Тест обработки невалидного периода."""
        with pytest.raises(ValueError, match="Invalid period"):
            await collector.get_dashboard_stats("invalid")

    async def test_metrics_structure(self, collector: MockStatCollector) -> None:
        """Тест структуры метрик."""
        stats = await collector.get_dashboard_stats("7d")

        # Проверяем total_messages
        assert hasattr(stats.metrics.total_messages, "value")
        assert hasattr(stats.metrics.total_messages, "change_percent")
        assert hasattr(stats.metrics.total_messages, "trend")
        assert hasattr(stats.metrics.total_messages, "description")
        assert stats.metrics.total_messages.trend in ["up", "down", "stable"]

        # Проверяем active_conversations
        assert hasattr(stats.metrics.active_conversations, "value")
        assert stats.metrics.active_conversations.trend in ["up", "down", "stable"]

        # Проверяем avg_conversation_length
        assert hasattr(stats.metrics.avg_conversation_length, "value")
        assert stats.metrics.avg_conversation_length.trend in ["up", "down", "stable"]

    async def test_time_series_structure(self, collector: MockStatCollector) -> None:
        """Тест структуры временного ряда."""
        stats = await collector.get_dashboard_stats("7d")

        for point in stats.time_series:
            assert hasattr(point, "date")
            assert hasattr(point, "value")
            assert isinstance(point.date, str)
            assert isinstance(point.value, int)
            assert point.value >= 0

    async def test_time_series_chronological_order(self, collector: MockStatCollector) -> None:
        """Тест хронологического порядка временного ряда."""
        stats = await collector.get_dashboard_stats("7d")

        dates = [point.date for point in stats.time_series]
        # Проверяем, что даты идут по возрастанию
        assert dates == sorted(dates)

    async def test_avg_conversation_length_calculation(self, collector: MockStatCollector) -> None:
        """Тест расчета средней длины диалога."""
        stats = await collector.get_dashboard_stats("7d")

        total_messages = stats.metrics.total_messages.value
        active_conversations = stats.metrics.active_conversations.value
        avg_length = stats.metrics.avg_conversation_length.value

        # Средняя длина должна быть примерно равна total / active
        expected_avg = total_messages / active_conversations
        # Проверяем с погрешностью из-за округления
        assert abs(avg_length - expected_avg) < 0.1

    async def test_deterministic_with_seed(self) -> None:
        """Тест детерминированности генерации с одинаковым seed."""
        # Создаем коллектор с фиксированным seed
        collector = MockStatCollector(seed=123)

        # Получаем статистику дважды
        stats1 = await collector.get_dashboard_stats("7d")

        # Создаем новый коллектор с тем же seed
        collector2 = MockStatCollector(seed=123)
        stats2 = await collector2.get_dashboard_stats("7d")

        # При одинаковом seed и одинаковом первом вызове результаты должны быть идентичными
        assert (
            stats1.metrics.total_messages.change_percent
            == stats2.metrics.total_messages.change_percent
        )
        assert (
            stats1.metrics.active_conversations.change_percent
            == stats2.metrics.active_conversations.change_percent
        )

    async def test_different_results_without_seed(self) -> None:
        """Тест различных результатов без фиксированного seed."""
        collector1 = MockStatCollector()
        collector2 = MockStatCollector()

        stats1 = await collector1.get_dashboard_stats("7d")
        stats2 = await collector2.get_dashboard_stats("7d")

        # Без seed результаты должны различаться (с высокой вероятностью)
        # Проверяем хотя бы одну метрику
        assert (
            stats1.metrics.total_messages.value != stats2.metrics.total_messages.value
            or stats1.metrics.active_conversations.value
            != stats2.metrics.active_conversations.value
        )

    async def test_positive_values(self, collector: MockStatCollector) -> None:
        """Тест положительных значений метрик."""
        stats = await collector.get_dashboard_stats("7d")

        assert stats.metrics.total_messages.value > 0
        assert stats.metrics.active_conversations.value > 0
        assert stats.metrics.avg_conversation_length.value >= 0

        for point in stats.time_series:
            assert point.value >= 0

    async def test_change_percent_range(self, collector: MockStatCollector) -> None:
        """Тест диапазона процентных изменений."""
        stats = await collector.get_dashboard_stats("7d")

        # Процентные изменения должны быть в разумных пределах
        assert -100 <= stats.metrics.total_messages.change_percent <= 100
        assert -100 <= stats.metrics.active_conversations.change_percent <= 100
        assert -100 <= stats.metrics.avg_conversation_length.change_percent <= 100
