"""add_source_field_to_messages

Revision ID: a1b2c3d4e5f6
Revises: e65a515f830d
Create Date: 2025-10-17 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "e65a515f830d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Добавление поля source в таблицу messages для различения источников сообщений."""
    # Добавляем колонку source со значением по умолчанию 'telegram'
    op.execute("""
        ALTER TABLE messages 
        ADD COLUMN source VARCHAR(20) NOT NULL DEFAULT 'telegram'
    """)

    # Создаем индекс для быстрой фильтрации по source
    op.execute("""
        CREATE INDEX idx_messages_source 
        ON messages(source)
    """)


def downgrade() -> None:
    """Откат миграции - удаление поля source и связанного индекса."""
    op.execute("DROP INDEX IF EXISTS idx_messages_source")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS source")

