"""FastAPI приложение для API дашборда и веб-чата."""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.protocols import StatCollectorProtocol
from src.api.real_stat_collector import RealStatCollector
from src.api.web_chat_handler import WebChatHandler
from src.database_conversation import DatabaseConversation
from src.protocols import LLMClientProtocol

# Глобальные экземпляры (будут инициализированы при запуске)
_stat_collector: StatCollectorProtocol | None = None
_web_chat_handler: WebChatHandler | None = None


def create_app(
    stat_collector: StatCollectorProtocol | None = None,
    llm_client: LLMClientProtocol | None = None,
    database_conversation: DatabaseConversation | None = None,
) -> FastAPI:
    """Создать и настроить FastAPI приложение.

    Args:
        stat_collector: Реализация сборщика статистики (если None, используется Real)
        llm_client: Клиент для работы с LLM (для веб-чата)
        database_conversation: Хранилище диалогов (для веб-чата)

    Returns:
        FastAPI: Настроенное приложение
    """
    app = FastAPI(
        title="Systech AIDD Dashboard & Chat API",
        description="API для дашборда статистики и веб-чата",
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

    # Устанавливаем глобальные зависимости
    global _stat_collector, _web_chat_handler

    _stat_collector = stat_collector or RealStatCollector()

    # Инициализируем WebChatHandler если предоставлены зависимости
    if llm_client and database_conversation:
        _web_chat_handler = WebChatHandler(
            database_conversation=database_conversation,
            llm_client=llm_client,
            max_history_messages=20,
        )

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


def get_web_chat_handler() -> WebChatHandler:
    """Dependency injection для WebChatHandler.

    Returns:
        WebChatHandler: Текущий экземпляр обработчика веб-чата

    Raises:
        RuntimeError: Если WebChatHandler не инициализирован
    """
    if _web_chat_handler is None:
        raise RuntimeError("WebChatHandler not initialized. Call create_app() with required dependencies first.")
    return _web_chat_handler
