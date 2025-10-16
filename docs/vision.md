# Техническое видение проекта

## 1. Технологии

### Основные технологии
- **Python 3.11+** - основной язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - фреймворк для Telegram Bot API (метод polling)
- **openai** (официальный клиент) - для работы с LLM через провайдер Openrouter
- **make** - автоматизация сборки, тестирования и проверки качества

### Инструменты качества кода (dev-зависимости)
- **ruff** - форматтер и линтер (замена black + flake8 + isort)
- **mypy** - статический анализатор типов (strict mode)
- **pytest** - фреймворк для тестирования
- **pytest-asyncio** - поддержка async тестов
- **pytest-cov** - измерение покрытия кода тестами

### Вспомогательные библиотеки
- **pydantic / pydantic-settings** - валидация конфигурации и данных
- **python-dotenv** - загрузка переменных окружения из .env файла (используется через pydantic)

### Хранение данных
- **PostgreSQL 16** - персистентное хранение истории диалогов
- **asyncpg** - асинхронный драйвер для PostgreSQL
- **Alembic** - управление миграциями базы данных
- **Docker Compose** - для локального окружения разработки

## 2. Принципы разработки

### Основные принципы
- **KISS (Keep It Simple, Stupid)** - максимальная простота, никакого оверинжиниринга
- **ООП** - строго 1 класс = 1 файл
- **Разделение ответственности** - каждый класс решает одну конкретную задачу
- **Явное лучше неявного** - понятный, читаемый код

### Подход к коду
- Async/await - асинхронное программирование (в соответствии с aiogram)
- **Type hints везде** - строгая типизация, mypy strict mode
- **Unit-тестирование** - минимум 70% coverage, pytest + pytest-asyncio
- **Форматирование и линтинг** - ruff format + ruff check перед коммитом
- **Protocol** - абстракции через typing.Protocol для DIP
- Минимум зависимостей между модулями

### Обработка ошибок
- Простое логирование ошибок в консоль
- Graceful degradation - бот продолжает работать при ошибках отдельных запросов
- Понятные сообщения пользователю при ошибках

## 3. Структура проекта

```
systech-aidd/
├── src/
│   ├── bot.py                   # Координация bot/dispatcher и регистрация обработчиков
│   ├── command_handler.py       # Обработчик команд бота (/start, /help, /clear, /role)
│   ├── message_handler.py       # Обработка текстовых сообщений пользователя
│   ├── llm_client.py            # Класс для работы с LLM через Openrouter
│   ├── conversation.py          # In-memory хранение истории (для тестов)
│   ├── database_conversation.py # PostgreSQL хранение истории (prod)
│   ├── database.py              # Connection pool и утилиты для asyncpg
│   ├── config.py                # Класс конфигурации (Pydantic BaseSettings)
│   ├── protocols.py             # Protocol интерфейсы для абстракций (DIP)
│   └── types.py                 # TypedDict для структур данных (ChatMessage)
├── alembic/
│   ├── versions/                # Миграции базы данных
│   ├── env.py                   # Конфигурация Alembic (async mode)
│   └── script.py.mako           # Шаблон для новых миграций
├── prompts/
│   └── nutritionist.txt         # Системный промпт для роли нутрициолога
├── tests/
│   ├── unit/                    # Unit-тесты модулей
│   ├── integration/             # Интеграционные тесты
│   └── conftest.py              # Pytest fixtures
├── main.py                      # Точка входа в приложение
├── docker-compose.yml           # PostgreSQL для локальной разработки
├── alembic.ini                  # Конфигурация Alembic
├── .env.example                 # Пример файла с переменными окружения
├── .env                         # Файл с переменными окружения (в .gitignore)
├── pyproject.toml               # Конфигурация uv, зависимости, инструменты качества
├── Makefile                     # Команды для сборки, тестирования, проверки качества
├── docs/                        # Документация проекта
└── README.md                    # Инструкции по запуску
```

### Основные модули

- **bot.py** - координация bot/dispatcher, регистрация обработчиков команд и сообщений
- **command_handler.py** - обработка команд бота (/start, /help, /clear, /role)
- **message_handler.py** - обработка текстовых сообщений от пользователя
- **llm_client.py** - взаимодействие с Openrouter через openai клиент, загрузка системного промпта
- **conversation.py** - управление историей диалога (в памяти, используется для тестов)
- **database_conversation.py** - управление историей диалога в PostgreSQL (production)
- **database.py** - утилиты для работы с asyncpg (connection pool, init_db, close_pool)
- **config.py** - загрузка и валидация конфигурации (Pydantic BaseSettings)
- **protocols.py** - Protocol интерфейсы для Dependency Inversion Principle
- **types.py** - TypedDict структуры данных (ChatMessage)

### Принцип организации
- 1 класс = 1 файл
- Каждый модуль отвечает за одну задачу
- Минимум зависимостей между модулями

## 4. Архитектура проекта

### Схема взаимодействия компонентов

```
User (Telegram) 
    ↓
TelegramBot (aiogram Bot + Dispatcher) 
    ↓                              ↓
CommandHandler              MessageHandler ← DatabaseConversation
    ↓                              ↓               (история)
(/start, /help, /clear)        LLMClient          ↓
                                   ↓           PostgreSQL
                             Openrouter API      (asyncpg)
```

### Поток обработки сообщения

1. **User** отправляет сообщение в Telegram
2. **Bot** получает сообщение через aiogram (polling)
3. **Bot** передает сообщение в **MessageHandler**
4. **MessageHandler** получает историю из **DatabaseConversation** по ключу (user_id, chat_id)
5. **DatabaseConversation** выполняет SQL запрос к PostgreSQL через asyncpg pool
6. **MessageHandler** формирует запрос к **LLMClient** (контекст + текущее сообщение)
7. **LLMClient** отправляет запрос в Openrouter и получает ответ
8. **MessageHandler** сохраняет user и assistant сообщения в **DatabaseConversation**
9. **DatabaseConversation** записывает сообщения в PostgreSQL (с метаданными)
10. **Bot** отправляет ответ пользователю

### Классы и их ответственность

- **Config** - хранит настройки (токены, модель LLM, лимиты, DATABASE_URL)
- **TelegramBot** - координация Bot/Dispatcher, регистрация обработчиков
- **CommandHandler** - обработка команд бота (/start, /help, /clear, /role)
- **MessageHandler** - координирует обработку текстовых сообщений
- **DatabaseConversation** - хранит и управляет историей диалогов в PostgreSQL (soft delete, последние N сообщений)
- **LLMClient** - загружает системный промпт из файла, отправляет запросы к LLM API
- **database.py** - управление connection pool, init_db(), close_pool()

### Protocol интерфейсы (DIP)

- **ConversationStorageProtocol** - абстракция для работы с историей диалогов
  - `add_message(user_id, chat_id, role, content)` - добавить сообщение
  - `get_history(user_id, chat_id)` - получить историю
  - `clear_history(user_id, chat_id)` - очистить историю
- **LLMClientProtocol** - абстракция для работы с LLM
  - `get_response(messages)` - получить ответ от LLM

### Команды бота

- **/start** - приветствие и инструкция
- **/help** - справка по доступным командам
- **/clear** - очистка истории диалога (альтернативное название: /new)
- **/role** - отображение текущей роли бота и его функций
- Любое текстовое сообщение - обработка через LLM с учетом роли

## 5. Модель данных

### Структура сообщения

Формат совместим с OpenAI API с дополнительными метаданными:
```python
{
    "role": "user" | "assistant",
    "content": "текст сообщения",
    "created_at": "2025-10-16T12:00:00",  # ISO 8601 формат
    "message_length": 13  # длина в символах
}
```

### Хранение истории диалогов

История диалогов хранится в PostgreSQL в таблице `messages`:

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_length INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL  -- Soft delete
);
```

**Стратегия Soft Delete:**
- Данные физически не удаляются из БД
- При "удалении" устанавливается `deleted_at = NOW()`
- При выборке фильтруются строки `WHERE deleted_at IS NULL`

### Класс DatabaseConversation

**Методы:**
- `add_message(user_id, chat_id, role, content)` - добавить сообщение в БД
- `get_history(user_id, chat_id)` - получить последние N сообщений (не удаленные)
- `clear_history(user_id, chat_id)` - soft delete истории диалога

**Логика:**
- Хранение в PostgreSQL (таблица `messages`)
- Async операции через asyncpg connection pool
- Raw SQL запросы (без ORM)
- Soft delete: `deleted_at IS NULL` для активных сообщений
- Лимит последних N сообщений через `ORDER BY created_at DESC LIMIT N`

## 6. Работа с LLM

### Класс LLMClient

**Основной метод:**
- `get_response(messages)` - отправить массив сообщений и получить ответ от LLM

**Реализация:**
- Использование официального клиента `openai` с настройкой на Openrouter
- Base URL: `https://openrouter.ai/api/v1`
- Передача API ключа Openrouter через заголовки
- Загрузка системного промпта из файла при инициализации
- Системный промпт автоматически добавляется в начало каждого запроса

### Формат запроса

```python
# Системный промпт + история диалога
messages = [
    {"role": "system", "content": "Ты профессиональный нутрициолог..."},  # Из файла
    {"role": "user", "content": "привет"},
    {"role": "assistant", "content": "Здравствуйте!"},
    {"role": "user", "content": "как дела?"}
]
```

### Параметры по умолчанию

- **model**: `anthropic/claude-3.5-sonnet` (Claude Sonnet 4.5)
- **messages**: системный промпт + история диалога из Conversation
- **temperature**: `0.7` (баланс между креативностью и последовательностью)
- **max_tokens**: `1000` (достаточно для развернутых ответов)

### Обработка ошибок

- При ошибке API - логирование и возврат сообщения об ошибке
- Таймаут запроса: 30 секунд
- Простое сообщение пользователю: "Извините, произошла ошибка. Попробуйте еще раз."

## 7. Сценарии работы

### Сценарий 1: Первый запуск

1. Пользователь отправляет `/start`
2. Бот отвечает приветствием и краткой инструкцией
3. Пользователь начинает диалог

### Сценарий 2: Обычный диалог

1. Пользователь отправляет текстовое сообщение
2. Бот показывает индикатор "печатает..."
3. Бот получает историю диалога (последние 10 сообщений)
4. Бот отправляет запрос в LLM с контекстом
5. Бот получает ответ и отправляет пользователю
6. Сообщения сохраняются в историю

### Сценарий 3: Помощь

1. Пользователь отправляет `/help`
2. Бот отправляет описание возможностей и команд

### Сценарий 4: Очистка истории

1. Пользователь отправляет `/clear` или `/new`
2. Бот выполняет soft delete истории диалога (устанавливает deleted_at)
3. Данные физически остаются в БД, но помечаются как удаленные
4. Бот подтверждает очистку сообщением
5. Следующий диалог начинается с чистого листа

### Сценарий 5: Отображение роли

1. Пользователь отправляет `/role`
2. Бот отправляет описание текущей роли и функций
3. Пользователь понимает, чем может помочь бот

### Сценарий 6: Обработка ошибок

1. Пользователь отправляет сообщение
2. Происходит ошибка при запросе к LLM
3. Бот логирует ошибку в консоль
4. Бот отправляет пользователю понятное сообщение об ошибке
5. История не сохраняется (можно повторить запрос)

## 8. Подход к конфигурированию

### Класс Config

**Реализация (Pydantic BaseSettings v2):**
- Наследование от **pydantic_settings.BaseSettings** для строгой валидации
- Автоматическая загрузка переменных окружения из `.env` через `model_config`
- Type-safe конфигурация с автоматическим приведением типов (str → int, str → float)
- Валидация обязательных параметров при инициализации (telegram_bot_token, openrouter_api_key)
- Pydantic типы: **PositiveInt**, **PositiveFloat** для числовых значений
- **Field** с constraints: `min_length`, `ge` (greater or equal), `le` (less or equal)
- Значения по умолчанию для необязательных параметров
- Понятные сообщения об ошибках валидации (**ValidationError**)
- Case-insensitive загрузка переменных окружения
- Игнорирование лишних полей (extra="ignore")

### Переменные окружения

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Openrouter API
OPENROUTER_API_KEY=your_openrouter_api_key

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://systech:systech_dev_password@localhost:5432/systech_aidd

# LLM Settings (опциональные, есть значения по умолчанию)
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=30

# System Prompt (опционально)
SYSTEM_PROMPT_PATH=prompts/nutritionist.txt

# Conversation (опционально)
MAX_HISTORY_MESSAGES=50
```

### Валидация

- **Обязательные**: `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`, `DATABASE_URL`
- **Опциональные**: все остальные (используются значения по умолчанию)
- При отсутствии обязательных параметров - ошибка при запуске

### Файл .env.example

- Содержит шаблон всех переменных окружения
- Пользователь копирует в `.env` и заполняет своими значениями
- `.env` добавлен в `.gitignore`

## 9. Подход к логгированию

### Реализация

**Используем стандартный модуль `logging` Python:**
- Вывод логов в консоль (stdout)
- Формат: `[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE`
- Уровень по умолчанию: `INFO`
- Настройка логгера при запуске приложения

### Что логируем

**INFO уровень:**
- Запуск бота
- Получение сообщения от пользователя (user_id, chat_id, текст сообщения)
- Отправка запроса к LLM (количество сообщений в контексте)
- Получение ответа от LLM (текст ответа)
- Успешная отправка ответа пользователю
- Выполнение команд (/start, /clear, /help)

**ERROR уровень:**
- Ошибки при запросе к LLM API (детали ошибки)
- Ошибки конфигурации при запуске
- Неожиданные исключения (stacktrace)

### Пример логов

```
[2025-10-10 12:00:00] [INFO] [bot] - Bot started successfully
[2025-10-10 12:00:15] [INFO] [message_handler] - Received message from user 123456 in chat 789012: "Привет"
[2025-10-10 12:00:16] [INFO] [llm_client] - Sending request to LLM with 1 messages
[2025-10-10 12:00:18] [INFO] [llm_client] - Received response: "Здравствуйте! Чем могу помочь?"
[2025-10-10 12:00:18] [INFO] [message_handler] - Response sent to user 123456
[2025-10-10 12:01:00] [ERROR] [llm_client] - LLM API error: Request timeout after 30s
```

### Особенности

- Простота: никаких файлов, ротации логов, только консоль
- Все важные события фиксируются для отладки
- Содержимое сообщений логируется для понимания контекста ошибок
- При необходимости можно перенаправить stdout в файл через shell

## 10. Тестирование

### Статистика тестирования

- **71 unit-тест** - все зеленые ✅
- **Coverage: 78%** (цель: ≥ 70%) ✅
- **Тестируемые модули**: config, conversation, database_conversation, database, llm_client, message_handler, command_handler

### Структура тестов

```
tests/
├── unit/
│   ├── test_config.py                  # 15 тестов (Pydantic валидация)
│   ├── test_conversation.py            # 11 тестов (in-memory история)
│   ├── test_database_conversation.py   # 9 тестов (PostgreSQL история, моки)
│   ├── test_database.py                # 6 тестов (normalize_database_url)
│   ├── test_llm_client.py              # 14 тестов (async API, моки)
│   ├── test_message_handler.py         # 6 тестов (Protocol моки)
│   └── test_command_handler.py         # 12 тестов (команды бота)
├── integration/                         # Будущее
└── conftest.py                          # Общие fixtures
```

### Используемые инструменты

- **pytest** ≥ 8.0.0 - фреймворк тестирования
- **pytest-asyncio** ≥ 0.24.0 - поддержка async/await (mode=auto)
- **pytest-cov** ≥ 6.0.0 - измерение coverage (fail-under=70)
- **pytest-mock** ≥ 3.12.0 - моки и патчи
- **unittest.mock** - AsyncMock, MagicMock, patch

### Примеры тестов

**Config (Pydantic валидация):**
```python
def test_config_missing_telegram_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверка ошибки при отсутствии обязательного параметра."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Config()
```

**LLMClient (async с моками):**
```python
async def test_get_response_success(llm_client: LLMClient) -> None:
    """Успешный запрос к LLM API."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Response"
    
    with patch.object(llm_client.client.chat.completions, "create", 
                      new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        response = await llm_client.get_response(messages)
        assert response == "Response"
```

**MessageHandler (Protocol моки):**
```python
async def test_handle_message(mock_llm: MagicMock, mock_conv: MagicMock) -> None:
    """Обработка сообщения с моками зависимостей."""
    handler = MessageHandler(llm_client=mock_llm, conversation=mock_conv)
    mock_llm.get_response.return_value = "Hi"
    
    response = await handler.handle_message(123, 456, "Hello")
    
    assert response == "Hi"
    mock_conv.add_message.assert_called()
```

### Команды тестирования

```bash
make test          # Запуск всех тестов
make test-cov      # Тесты с coverage report
make quality       # Полная проверка (format + lint + typecheck + test)
```

### Coverage report

```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/__init__.py                    0      0   100%
src/bot.py                        35     35     0%   # Точка входа, не тестируется
src/command_handler.py            31      0   100%
src/config.py                     13      0   100%
src/conversation.py               27      0   100%
src/database.py                   35     23    34%   42-52, 64-66, 73-77, 89-102
src/database_conversation.py      31      0   100%
src/llm_client.py                 57      0   100%
src/message_handler.py            17      0   100%
src/protocols.py                   8      0   100%
src/types.py                       6      0   100%
------------------------------------------------------------
TOTAL                            260     58    78%
```

