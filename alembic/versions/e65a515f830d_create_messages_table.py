"""create_messages_table

Revision ID: e65a515f830d
Revises:
Create Date: 2025-10-16 15:05:53.466194

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e65a515f830d"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Создание таблицы messages для хранения истории диалогов."""
    # Создаем таблицу messages
    op.execute("""
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            chat_id BIGINT NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            message_length INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """)

    # Индекс для быстрого поиска по пользователю и чату с учетом deleted_at
    op.execute("""
        CREATE INDEX idx_user_chat_deleted 
        ON messages(user_id, chat_id, deleted_at)
    """)

    # Частичный индекс для фильтрации только активных сообщений
    op.execute("""
        CREATE INDEX idx_deleted_at 
        ON messages(deleted_at) 
        WHERE deleted_at IS NULL
    """)


def downgrade() -> None:
    """Откат миграции - удаление таблицы messages."""
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
