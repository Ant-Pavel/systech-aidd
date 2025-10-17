"""Entrypoint для запуска API сервера дашборда."""

import logging

import uvicorn

from src.api.app import create_app
from src.api.mock_stat_collector import MockStatCollector

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Запуск API сервера."""
    logger.info("Starting Dashboard API server...")

    # Создаем приложение с Mock сборщиком статистики
    stat_collector = MockStatCollector()
    app = create_app(stat_collector=stat_collector)

    logger.info("Using MockStatCollector for statistics")
    logger.info("API documentation available at: http://localhost:8000/docs")
    logger.info("ReDoc documentation available at: http://localhost:8000/redoc")

    # Запускаем сервер
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
