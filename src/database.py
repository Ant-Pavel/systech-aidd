"""Модуль для работы с PostgreSQL через asyncpg."""

import logging

import asyncpg  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# Глобальный connection pool
_pool: asyncpg.Pool | None = None  # type: ignore[no-any-unimported]


def normalize_database_url(database_url: str) -> str:
    """Нормализовать database URL для asyncpg.

    SQLAlchemy использует формат postgresql+asyncpg://, но asyncpg принимает только
    postgresql:// или postgres://. Эта функция конвертирует URL при необходимости.

    Args:
        database_url: Connection string (может быть в SQLAlchemy или asyncpg формате)

    Returns:
        str: URL в формате, совместимом с asyncpg
    """
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return database_url


async def create_pool(database_url: str) -> asyncpg.Pool:  # type: ignore[no-any-unimported]
    """Создать connection pool для PostgreSQL.

    Args:
        database_url: Connection string для PostgreSQL

    Returns:
        asyncpg.Pool: Connection pool
    """
    global _pool

    # Нормализуем URL для asyncpg
    normalized_url = normalize_database_url(database_url)

    logger.info("Creating database connection pool")
    _pool = await asyncpg.create_pool(
        normalized_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )
    logger.info("Database connection pool created successfully")
    return _pool


async def get_pool() -> asyncpg.Pool:  # type: ignore[no-any-unimported]
    """Получить текущий connection pool.

    Returns:
        asyncpg.Pool: Connection pool

    Raises:
        RuntimeError: Если pool не инициализирован
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call create_pool() first.")
    return _pool


async def close_pool() -> None:
    """Закрыть connection pool."""
    global _pool

    if _pool is not None:
        logger.info("Closing database connection pool")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


async def init_db(database_url: str) -> None:
    """Инициализировать подключение к БД и проверить доступность.

    Args:
        database_url: Connection string для PostgreSQL

    Raises:
        Exception: Если не удалось подключиться к БД
    """
    logger.info("Initializing database connection")

    try:
        await create_pool(database_url)
        pool = await get_pool()

        # Проверяем подключение
        async with pool.acquire() as connection:
            version = await connection.fetchval("SELECT version()")
            logger.info(f"Successfully connected to database: {version}")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
