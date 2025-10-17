"""FastAPI приложение для API дашборда."""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.mock_stat_collector import MockStatCollector
from src.api.protocols import StatCollectorProtocol

# Глобальный экземпляр StatCollector (будет инициализирован при запуске)
_stat_collector: StatCollectorProtocol | None = None


def create_app(stat_collector: StatCollectorProtocol | None = None) -> FastAPI:
    """Создать и настроить FastAPI приложение.

    Args:
        stat_collector: Реализация сборщика статистики (если None, используется Mock)

    Returns:
        FastAPI: Настроенное приложение
    """
    app = FastAPI(
        title="Systech AIDD Dashboard API",
        description="API для предоставления статистики по диалогам Telegram-бота",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Настройка CORS для frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",  # Next.js alternative port
            "http://localhost:5173",  # Vite dev server
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Устанавливаем глобальный stat_collector
    global _stat_collector
    _stat_collector = stat_collector or MockStatCollector()

    # Регистрируем роуты
    from src.api.routes import router

    app.include_router(router)

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, Any]:
        """Проверка состояния API.

        Returns:
            dict: Статус сервиса
        """
        return {"status": "ok", "service": "dashboard-api", "version": "1.0.0"}

    return app


def get_stat_collector() -> StatCollectorProtocol:
    """Dependency injection для StatCollector.

    Returns:
        StatCollectorProtocol: Текущий экземпляр сборщика статистики

    Raises:
        RuntimeError: Если StatCollector не инициализирован
    """
    if _stat_collector is None:
        raise RuntimeError("StatCollector not initialized. Call create_app() first.")
    return _stat_collector
