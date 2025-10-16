"""Unit tests для database.py - работа с PostgreSQL через asyncpg."""

from src.database import normalize_database_url


class TestNormalizeDatabaseUrl:
    """Тесты для normalize_database_url."""

    def test_normalize_sqlalchemy_url(self) -> None:
        """SQLAlchemy формат URL конвертируется в asyncpg формат."""
        # Arrange
        sqlalchemy_url = "postgresql+asyncpg://user:pass@localhost:5432/db"
        expected = "postgresql://user:pass@localhost:5432/db"

        # Act
        result = normalize_database_url(sqlalchemy_url)

        # Assert
        assert result == expected

    def test_normalize_asyncpg_url_unchanged(self) -> None:
        """asyncpg формат URL остается без изменений."""
        # Arrange
        asyncpg_url = "postgresql://user:pass@localhost:5432/db"

        # Act
        result = normalize_database_url(asyncpg_url)

        # Assert
        assert result == asyncpg_url

    def test_normalize_postgres_scheme(self) -> None:
        """postgres:// схема остается без изменений."""
        # Arrange
        postgres_url = "postgres://user:pass@localhost:5432/db"

        # Act
        result = normalize_database_url(postgres_url)

        # Assert
        assert result == postgres_url

    def test_normalize_with_special_characters(self) -> None:
        """URL со специальными символами обрабатывается корректно."""
        # Arrange
        sqlalchemy_url = "postgresql+asyncpg://user:p@ss!word@localhost:5432/my-db_123"
        expected = "postgresql://user:p@ss!word@localhost:5432/my-db_123"

        # Act
        result = normalize_database_url(sqlalchemy_url)

        # Assert
        assert result == expected

    def test_normalize_with_query_params(self) -> None:
        """URL с query параметрами обрабатывается корректно."""
        # Arrange
        sqlalchemy_url = "postgresql+asyncpg://user:pass@localhost:5432/db?sslmode=require"
        expected = "postgresql://user:pass@localhost:5432/db?sslmode=require"

        # Act
        result = normalize_database_url(sqlalchemy_url)

        # Assert
        assert result == expected

    def test_normalize_only_first_occurrence(self) -> None:
        """Заменяется только первое вхождение postgresql+asyncpg://."""
        # Arrange
        # (хотя такой URL невалиден, проверяем корректность замены)
        weird_url = "postgresql+asyncpg://user:postgresql+asyncpg://pass@localhost:5432/db"
        expected = "postgresql://user:postgresql+asyncpg://pass@localhost:5432/db"

        # Act
        result = normalize_database_url(weird_url)

        # Assert
        assert result == expected
