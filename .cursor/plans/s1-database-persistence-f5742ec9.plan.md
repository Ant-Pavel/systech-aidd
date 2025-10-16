<!-- f5742ec9-52b1-44a2-834a-3c77d558e792 49266fc1-90da-4736-abb1-719e0152fffd -->
# S1: Персистентное хранение данных

## Технические решения

### СУБД

- **PostgreSQL 16** - production-ready СУБД
- Запуск через Docker Compose
- Настройки: база `systech_aidd`, пользователь `systech`, порт `5432`
- Volume для персистентности данных между перезапусками

### Способ работы с БД

- **Драйвер: asyncpg** - асинхронный нативный драйвер для PostgreSQL
- **Raw SQL** - прямые SQL запросы без ORM (максимальная прозрачность и контроль)
- **Асинхронные запросы** - все операции через `await`, не блокируют event loop
- **Connection pool** - `asyncpg.create_pool()` для переиспользования соединений
- **API методы**:
  - `pool.execute(query, *args)` - INSERT/UPDATE/DELETE
  - `pool.fetch(query, *args)` - SELECT (возвращает список записей)
  - `pool.fetchrow(query, *args)` - SELECT (возвращает одну запись)
- **SQL запросы**:
  - `INSERT INTO messages (...) VALUES ($1, $2, ...) RETURNING id` - добавление сообщений
  - `SELECT * FROM messages WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT $1` - получение истории
  - `UPDATE messages SET deleted_at = NOW() WHERE user_id = $1 AND chat_id = $2` - soft delete

### Система миграций

- **Alembic** - индустриальный стандарт для миграций
- **Async режим** - работа через SQLAlchemy async engine
- **Versioning** - каждая миграция имеет номер и зависимости
- Процесс:

  1. `alembic revision -m "description"` - создать новую миграцию
  2. Написать SQL в `upgrade()` и `downgrade()`
  3. `alembic upgrade head` - применить все миграции
  4. `alembic downgrade -1` - откатить последнюю миграцию

- Миграции хранятся в `alembic/versions/`
- История миграций в таблице `alembic_version`

## 1. Подготовка инфраструктуры

### 1.1 Docker окружение

- Создать `docker-compose.yml` с PostgreSQL 16
- Настроить volume для персистентности данных
- Добавить healthcheck для проверки готовности БД
- Порт: 5432, база: systech_aidd, пользователь: systech

### 1.2 Зависимости

Добавить в `pyproject.toml`:

- `asyncpg>=0.29.0` - асинхронный драйвер PostgreSQL (быстрый, нативный)
- `alembic>=1.13.0` - система миграций
- `sqlalchemy>=2.0.0` - требуется для async поддержки Alembic

Обновить `.env.example` и `src/config.py`:

- `DATABASE_URL` - connection string для PostgreSQL (формат: `postgresql+asyncpg://user:password@host:port/database`)

## 2. Настройка Alembic

### 2.1 Инициализация

- Запустить `alembic init alembic`
- Настроить `alembic.ini` для использования DATABASE_URL из конфига
- Настроить `alembic/env.py` для работы с Config класса

### 2.2 Создание первой миграции

Таблица `messages`:

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_length INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    INDEX idx_user_chat (user_id, chat_id),
    INDEX idx_deleted_at (deleted_at)
);
```

## 3. Слой доступа к данным (TDD)

### 3.1 Обновить типы данных

`src/types.py` - добавить поля в `ChatMessage`:

```python
class ChatMessage(TypedDict):
    role: str
    content: str
    created_at: str  # ISO 8601 формат
    message_length: int
```

### 3.2 Создать DatabaseConversation

Новый файл `src/database_conversation.py`:

- Реализовать `ConversationStorageProtocol`
- Методы: `add_message`, `get_history`, `clear_history` (soft delete)
- Использовать raw SQL через asyncpg
- Connection pool для управления соединениями
- `get_history` возвращает только не удаленные сообщения (deleted_at IS NULL)
- Лимит последних N сообщений в `get_history`

### 3.3 Database helper

Новый файл `src/database.py`:

- Функция `create_pool()` для создания connection pool
- Функция `init_db()` для проверки подключения при старте
- Функция `close_pool()` для graceful shutdown

## 4. Тесты (TDD подход)

### 4.1 Unit тесты

`tests/unit/test_database_conversation.py`:

- Тестировать DatabaseConversation с мокированием asyncpg
- Проверка SQL запросов (add, get, clear)
- Soft delete: deleted_at устанавливается, данные не удаляются
- Изоляция данных между пользователями
- Лимит истории

## 5. Рефакторинг приложения

### 5.1 Обновить Config

`src/config.py`:

- Добавить `database_url: str` (обязательное поле)
- Валидация формата connection string

### 5.2 Обновить main.py

- Инициализировать DatabaseConversation вместо Conversation
- Проверить подключение к БД при старте через `init_db()`
- Graceful shutdown для закрытия соединений

### 5.3 Обратная совместимость

- Оставить `src/conversation.py` (in-memory) для локальной разработки
- Выбор реализации через переменную окружения (опционально)

## 6. Документация

### 6.1 ADR документ

Создать `docs/adr/0001-postgresql-raw-sql-alembic.md`:

- Контекст: почему PostgreSQL
- Решение: raw SQL вместо ORM
- Последствия: плюсы и минусы выбора

### 6.2 Обновить guides

- `docs/guides/07_configuration_secrets.md` - добавить DATABASE_URL
- `docs/guides/01_getting_started.md` - инструкции по запуску PostgreSQL
- Создать `docs/guides/10_database_migrations.md` - работа с Alembic

### 6.3 Обновить README

- Добавить инструкции по запуску Docker
- Команды для применения миграций

## Основные файлы

- `docker-compose.yml` (новый)
- `pyproject.toml` (зависимости)
- `.env.example` (DATABASE_URL)
- `src/config.py` (database_url поле)
- `src/types.py` (расширить ChatMessage)
- `src/database.py` (новый)
- `src/database_conversation.py` (новый)
- `main.py` (использовать DatabaseConversation)
- `alembic/versions/xxxx_create_messages_table.py` (миграция)

## Принципы

- KISS: простые SQL запросы без сложных JOIN
- TDD: сначала тесты, потом код
- Soft delete: deleted_at вместо DELETE
- Raw SQL: прозрачность и контроль
- Connection pooling: эффективное использование соединений

### To-dos

- [ ] Создать docker-compose.yml с PostgreSQL 16
- [ ] Обновить .env.example с DATABASE_URL
- [ ] Добавить asyncpg, alembic, sqlalchemy в pyproject.toml
- [ ] Инициализировать Alembic и настроить конфигурацию
- [ ] Создать миграцию для таблицы messages с полями для soft delete
- [ ] Расширить ChatMessage типом created_at и message_length
- [ ] Создать database.py с функциями подключения и инициализации
- [ ] Добавить database_url в Config с валидацией
- [ ] Реализовать DatabaseConversation с raw SQL (TDD)
- [ ] Обновить main.py для использования DatabaseConversation
- [ ] Создать ADR документ 0001-postgresql-raw-sql-alembic.md
- [ ] Обновить guides (01, 07) и создать guide 10 по миграциям
- [ ] Актуализировать vision.md и idea.md на соответствие изменениям
- [ ] Добавить ссылку на план в таблицу спринтов в roadmap.md
- [ ] Обновить README.md с инструкциями по Docker и миграциям