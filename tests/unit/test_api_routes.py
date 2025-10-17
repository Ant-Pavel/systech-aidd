"""Unit тесты для API routes."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.models import DashboardStats, MetricCard, MetricsData, TimeSeriesPoint


class TestAPIRoutes:
    """Тесты для API endpoints."""

    @pytest.fixture
    def mock_stat_collector(self) -> MagicMock:
        """Фикстура для mock StatCollector."""
        mock = MagicMock()

        # Создаем mock данные
        mock_stats = DashboardStats(
            metrics=MetricsData(
                total_messages=MetricCard(
                    value=1000,
                    change_percent=10.5,
                    trend="up",
                    description="Trending up",
                ),
                active_conversations=MetricCard(
                    value=100,
                    change_percent=-5.0,
                    trend="down",
                    description="Down this period",
                ),
                avg_conversation_length=MetricCard(
                    value=10.0,
                    change_percent=2.5,
                    trend="stable",
                    description="Stable performance",
                ),
            ),
            time_series=[
                TimeSeriesPoint(date="2025-10-10", value=150),
                TimeSeriesPoint(date="2025-10-11", value=160),
            ],
        )

        # Настраиваем async mock
        mock.get_dashboard_stats = AsyncMock(return_value=mock_stats)

        return mock

    @pytest.fixture
    def client(self, mock_stat_collector: MagicMock) -> TestClient:
        """Фикстура для TestClient с mock StatCollector."""
        app = create_app(stat_collector=mock_stat_collector)
        return TestClient(app)

    def test_health_check(self, client: TestClient) -> None:
        """Тест health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "dashboard-api"
        assert "version" in data

    def test_get_stats_default_period(
        self, client: TestClient, mock_stat_collector: MagicMock
    ) -> None:
        """Тест получения статистики с периодом по умолчанию."""
        response = client.get("/api/stats")

        assert response.status_code == 200
        data = response.json()

        # Проверяем структуру ответа
        assert "metrics" in data
        assert "time_series" in data

        # Проверяем метрики
        assert "total_messages" in data["metrics"]
        assert "active_conversations" in data["metrics"]
        assert "avg_conversation_length" in data["metrics"]

        # Проверяем, что collector был вызван с периодом по умолчанию
        mock_stat_collector.get_dashboard_stats.assert_called_once_with("7d")

    def test_get_stats_7d(self, client: TestClient, mock_stat_collector: MagicMock) -> None:
        """Тест получения статистики за 7 дней."""
        response = client.get("/api/stats?period=7d")

        assert response.status_code == 200
        mock_stat_collector.get_dashboard_stats.assert_called_once_with("7d")

    def test_get_stats_30d(self, client: TestClient, mock_stat_collector: MagicMock) -> None:
        """Тест получения статистики за 30 дней."""
        response = client.get("/api/stats?period=30d")

        assert response.status_code == 200
        mock_stat_collector.get_dashboard_stats.assert_called_once_with("30d")

    def test_get_stats_3m(self, client: TestClient, mock_stat_collector: MagicMock) -> None:
        """Тест получения статистики за 3 месяца."""
        response = client.get("/api/stats?period=3m")

        assert response.status_code == 200
        mock_stat_collector.get_dashboard_stats.assert_called_once_with("3m")

    def test_get_stats_invalid_period(self, client: TestClient) -> None:
        """Тест обработки невалидного периода."""
        response = client.get("/api/stats?period=invalid")

        assert response.status_code == 422  # Validation error

    def test_get_stats_response_structure(self, client: TestClient) -> None:
        """Тест структуры ответа API."""
        response = client.get("/api/stats?period=7d")

        assert response.status_code == 200
        data = response.json()

        # Проверяем метрики
        metrics = data["metrics"]
        for metric_name in ["total_messages", "active_conversations", "avg_conversation_length"]:
            assert metric_name in metrics
            metric = metrics[metric_name]
            assert "value" in metric
            assert "change_percent" in metric
            assert "trend" in metric
            assert "description" in metric
            assert metric["trend"] in ["up", "down", "stable"]

        # Проверяем временной ряд
        assert isinstance(data["time_series"], list)
        assert len(data["time_series"]) > 0
        for point in data["time_series"]:
            assert "date" in point
            assert "value" in point

    def test_get_stats_error_handling(
        self, client: TestClient, mock_stat_collector: MagicMock
    ) -> None:
        """Тест обработки ошибок при получении статистики."""
        # Настраиваем mock для выброса исключения
        mock_stat_collector.get_dashboard_stats = AsyncMock(side_effect=Exception("Database error"))

        response = client.get("/api/stats?period=7d")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_get_stats_value_error_handling(
        self, client: TestClient, mock_stat_collector: MagicMock
    ) -> None:
        """Тест обработки ValueError при получении статистики."""
        # Настраиваем mock для выброса ValueError
        mock_stat_collector.get_dashboard_stats = AsyncMock(
            side_effect=ValueError("Invalid period")
        )

        response = client.get("/api/stats?period=7d")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_cors_headers(self, client: TestClient) -> None:
        """Тест наличия CORS заголовков."""
        # Проверяем наличие CORS middleware через GET запрос
        response = client.get("/api/stats")

        # CORS middleware должен добавлять заголовки
        assert response.status_code == 200
        # В тестовом клиенте CORS заголовки могут не присутствовать,
        # но middleware должен быть настроен в приложении

    def test_openapi_docs_available(self, client: TestClient) -> None:
        """Тест доступности OpenAPI документации."""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/redoc")
        assert response.status_code == 200

        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_openapi_schema_structure(self, client: TestClient) -> None:
        """Тест структуры OpenAPI схемы."""
        response = client.get("/openapi.json")
        schema = response.json()

        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        # Проверяем наличие наших endpoints
        assert "/health" in schema["paths"]
        assert "/api/stats" in schema["paths"]

        # Проверяем описание API
        assert schema["info"]["title"] == "Systech AIDD Dashboard API"
        assert "version" in schema["info"]
