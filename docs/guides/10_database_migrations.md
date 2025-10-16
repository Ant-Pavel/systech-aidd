# Руководство по работе с миграциями базы данных

## Введение

Проект использует **PostgreSQL** для хранения истории диалогов и **Alembic** для управления миграциями схемы базы данных.

## Технологии

- **PostgreSQL 16** - СУБД
- **asyncpg** - асинхронный драйвер
- **Alembic** - система миграций
- **Docker Compose** - для локального окружения

## Запуск PostgreSQL

### Локальная разработка

1. Убедитесь, что Docker запущен

2. Запустите PostgreSQL через Docker Compose:
```bash
docker-compose up -d
```

3. Проверьте статус:
```bash
docker-compose ps
```

4. Просмотр логов:
```bash
docker-compose logs postgres
```

5. Остановка:
```bash
docker-compose down
```

### Подключение к БД

Connection string в `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://systech:systech_dev_password@localhost:5432/systech_aidd
```

## Работа с миграциями

### Применение миграций

Применить все миграции (upgrade to head):
```bash
uv run alembic upgrade head
```

### Создание новой миграции

1. Создать файл миграции:
```bash
uv run alembic revision -m "описание_изменений"
```

2. Отредактировать созданный файл в `alembic/versions/`

3. Написать SQL в функции `upgrade()` и `downgrade()`

Пример:
```python
def upgrade() -> None:
    """Описание изменений."""
    op.execute("""
        CREATE TABLE example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    """)

def downgrade() -> None:
    """Откат изменений."""
    op.execute("DROP TABLE IF EXISTS example CASCADE")
```

### Откат миграций

Откатить последнюю миграцию:
```bash
uv run alembic downgrade -1
```

Откатить до конкретной версии:
```bash
uv run alembic downgrade <revision_id>
```

Откатить все миграции:
```bash
uv run alembic downgrade base
```

### Просмотр истории миграций

Текущая версия БД:
```bash
uv run alembic current
```

История миграций:
```bash
uv run alembic history
```

Подробная информация:
```bash
uv run alembic history --verbose
```

## Структура базы данных

### Таблица messages

Хранит историю диалогов с поддержкой soft delete.

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_length INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);
```

**Индексы:**
- `idx_user_chat_deleted` - для быстрого поиска по user_id, chat_id, deleted_at
- `idx_deleted_at` - частичный индекс для активных сообщений (WHERE deleted_at IS NULL)

**Поля:**
- `id` - уникальный идентификатор
- `user_id` - ID пользователя Telegram
- `chat_id` - ID чата Telegram
- `role` - роль отправителя ('user' или 'assistant')
- `content` - текст сообщения
- `message_length` - длина сообщения в символах
- `created_at` - дата и время создания
- `deleted_at` - дата и время удаления (soft delete, NULL = активное)

## Soft Delete стратегия

Данные **не удаляются физически** из БД. Вместо этого:

1. При "удалении" устанавливается `deleted_at = NOW()`
2. При выборке фильтруются строки `WHERE deleted_at IS NULL`
3. Преимущества:
   - Возможность восстановления данных
   - Аудит и аналитика
   - Соответствие требованиям регуляторов

## Прямое подключение к БД

### Через psql (Docker)

```bash
docker-compose exec postgres psql -U systech -d systech_aidd
```

### Полезные SQL команды

Просмотр таблиц:
```sql
\dt
```

Структура таблицы:
```sql
\d messages
```

Просмотр индексов:
```sql
\di
```

Количество сообщений:
```sql
SELECT COUNT(*) FROM messages WHERE deleted_at IS NULL;
```

Последние сообщения:
```sql
SELECT * FROM messages 
WHERE deleted_at IS NULL 
ORDER BY created_at DESC 
LIMIT 10;
```

## Troubleshooting

### Ошибка подключения к БД

1. Проверьте что Docker запущен:
```bash
docker ps
```

2. Проверьте что PostgreSQL запущен:
```bash
docker-compose ps
```

3. Проверьте DATABASE_URL в `.env`

### Миграции не применяются

1. Проверьте текущую версию:
```bash
uv run alembic current
```

2. Проверьте историю:
```bash
uv run alembic history
```

3. Попробуйте применить конкретную миграцию:
```bash
uv run alembic upgrade <revision_id>
```

### Сброс БД (осторожно!)

```bash
# Остановить контейнеры
docker-compose down

# Удалить volumes (ВСЕ ДАННЫЕ БУДУТ ПОТЕРЯНЫ!)
docker-compose down -v

# Запустить заново
docker-compose up -d

# Применить миграции
uv run alembic upgrade head
```

## Best Practices

1. **Всегда тестируйте миграции** на локальной БД перед production
2. **Пишите downgrade()** для возможности отката
3. **Делайте резервные копии** перед применением миграций в production
4. **Одна миграция - одно изменение** (для упрощения откатов)
5. **Документируйте изменения** в docstring миграции
6. **Проверяйте производительность** - добавляйте EXPLAIN ANALYZE для сложных запросов

## Ссылки

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)


