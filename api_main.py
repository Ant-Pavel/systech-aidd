"""Entrypoint для запуска API сервера дашборда и веб-чата."""

import asyncio
import logging

import uvicorn

from src.api.app import create_app
from src.api.real_stat_collector import RealStatCollector
from src.config import Config
from src.database import close_pool, init_db
from src.database_conversation import DatabaseConversation
from src.llm_client import LLMClient

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Запуск API сервера."""
    logger.info("Starting Dashboard & Chat API server...")

    config = Config()

    try:
        # Инициализируем подключение к БД
        logger.info("Initializing database connection...")
        await init_db(config.database_url)
        logger.info("Database connection initialized successfully")

        # Инициализируем LLM клиент для веб-чата
        llm_client = LLMClient(
            api_key=config.openrouter_api_key,
            model=config.llm_model,
            temperature=config.llm_temperature,
            max_tokens=config.llm_max_tokens,
            timeout=config.llm_timeout,
            system_prompt_path=config.system_prompt_path,
        )

        # Инициализируем хранилище истории диалогов
        database_conversation = DatabaseConversation(config.max_history_messages)

        # Создаем сборщик реальной статистики
        stat_collector = RealStatCollector()

        # Создаем приложение со всеми зависимостями
        app = create_app(
            stat_collector=stat_collector,
            llm_client=llm_client,
            database_conversation=database_conversation,
        )

        logger.info("Using RealStatCollector for statistics (database-backed)")
        logger.info("Web chat handler initialized with LLM client")
        logger.info("API documentation available at: http://localhost:8000/docs")
        logger.info("ReDoc documentation available at: http://localhost:8000/redoc")

        # Создаем конфигурацию uvicorn
        config_uvicorn = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
        )
        server = uvicorn.Server(config_uvicorn)

        # Запускаем сервер
        await server.serve()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        # Graceful shutdown - закрываем connection pool
        logger.info("Closing database connection...")
        await close_pool()
        logger.info("API server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
