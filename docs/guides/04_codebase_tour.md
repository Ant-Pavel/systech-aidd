# Codebase Tour

Guided tour по структуре кода проекта.

## Project Structure

```
systech-aidd/
├── main.py                  # 🚀 Точка входа
├── src/                     # 📦 Исходный код
│   ├── bot.py              # Telegram bot координация
│   ├── command_handler.py  # Обработка команд
│   ├── message_handler.py  # Обработка сообщений
│   ├── llm_client.py       # LLM API клиент
│   ├── conversation.py     # История диалогов
│   ├── config.py           # Конфигурация
│   ├── protocols.py        # Protocol интерфейсы
│   └── types.py            # TypedDict структуры
├── tests/                   # 🧪 Тесты
│   ├── unit/               # Unit-тесты
│   └── conftest.py         # Pytest fixtures
├── prompts/                 # 📝 Системные промпты
│   └── nutritionist.txt    # Роль нутрициолога
├── docs/                    # 📚 Документация
├── pyproject.toml          # ⚙️ Конфигурация проекта
├── Makefile                # 🔧 Команды сборки
├── .env                    # 🔐 Секреты (не в git)
└── uv.lock                 # 📌 Locked dependencies
```

## Entry Point

### `main.py` - Точка входа приложения

**Назначение:** Инициализация и запуск бота

**Что делает:**
1. Настраивает логирование
2. Создает `Config` из `.env`
3. Инициализирует зависимости в правильном порядке
4. Запускает бота в polling режиме

**Ключевой код:**
```python
config = Config()                                    # 1. Конфигурация
llm_client = LLMClient(...)                         # 2. LLM клиент
conversation = Conversation(...)                     # 3. История
command_handler = CommandHandler(conversation)       # 4. Обработчик команд
message_handler = MessageHandler(llm_client, conversation)  # 5. Обработчик сообщений
bot = TelegramBot(token, command_handler, message_handler)  # 6. Бот
await bot.start()                                    # 7. Запуск
```

## Core Modules

### `src/bot.py` - TelegramBot

**Ответственность:** Координация aiogram компонентов

**Публичный API:**
- `__init__(token, command_handler, message_handler)` - инициализация
- `start()` - запуск polling

**Что делает:**
- Создает `Bot` и `Dispatcher` из aiogram
- Регистрирует обработчики команд и сообщений
- Показывает индикатор "печатает..." при обработке
- Обрабатывает ошибки gracefully

**Ключевые методы:**
```python
def _register_handlers(self) -> None:
    """Регистрация всех обработчиков."""
    self.dp.message(Command("start"))(self.command_handler.start)
    self.dp.message(Command("help"))(self.command_handler.help)
    # ...
```

---

### `src/command_handler.py` - CommandHandler

**Ответственность:** Обработка команд бота

**Зависимости:**
- `ConversationStorageProtocol` - для команды `/clear`

**Команды:**
- `/start` - приветствие с описанием роли
- `/help` - список команд
- `/clear` или `/new` - очистка истории
- `/role` - описание роли нутрициолога

**Пример команды:**
```python
async def clear(self, message: Message) -> None:
    """Команда /clear - очистка истории."""
    self.conversation.clear_history(user_id, chat_id)
    await message.answer("✅ История очищена!")
```

---

### `src/message_handler.py` - MessageHandler

**Ответственность:** Обработка текстовых сообщений

**Зависимости:**
- `LLMClientProtocol` - получение ответа от LLM
- `ConversationStorageProtocol` - работа с историей

**Flow обработки:**
1. Получить историю диалога
2. Добавить текущее сообщение
3. Отправить в LLM
4. Сохранить user message и assistant response
5. Вернуть ответ

**Ключевой метод:**
```python
async def handle_message(self, user_id: int, chat_id: int, text: str) -> str:
    history = self.conversation.get_history(user_id, chat_id)
    messages = [*history, ChatMessage(role="user", content=text)]
    response = await self.llm_client.get_response(messages)
    self.conversation.add_message(user_id, chat_id, "user", text)
    self.conversation.add_message(user_id, chat_id, "assistant", response)
    return response
```

---

### `src/llm_client.py` - LLMClient

**Ответственность:** Интеграция с Openrouter API

**Зависимости:**
- `openai.AsyncOpenAI` - клиент для API

**Функционал:**
- Загрузка системного промпта из файла при инициализации
- Добавление system message в начало каждого запроса
- Обработка специфичных ошибок API (timeout, auth, rate limit)

**Ключевые параметры:**
- `base_url` - `https://openrouter.ai/api/v1`
- `model` - по умолчанию `openai/gpt-oss-20b:free`
- `temperature` - `0.7`
- `max_tokens` - `1000`
- `timeout` - `30` секунд

**Error handling:**
```python
except APITimeoutError:
    raise Exception("Timeout: Запрос превысил лимит времени")
except AuthenticationError:
    raise Exception("Authentication error: Проверьте API ключ")
except RateLimitError:
    raise Exception("Rate limit: Превышен лимит запросов")
```

---

### `src/conversation.py` - Conversation

**Ответственность:** Хранение истории диалогов в памяти

**Структура данных:**
```python
conversations: dict[tuple[int, int], list[ChatMessage]]
# Ключ: (user_id, chat_id)
# Значение: список последних 10 сообщений
```

**Публичный API:**
- `add_message(user_id, chat_id, role, content)` - добавить сообщение
- `get_history(user_id, chat_id)` - получить историю
- `clear_history(user_id, chat_id)` - очистить историю

**Логика лимита:**
```python
if len(self.conversations[key]) > self.max_history_messages:
    self.conversations[key] = self.conversations[key][-self.max_history_messages:]
```

---

### `src/config.py` - Config

**Ответственность:** Загрузка и валидация конфигурации

**Технология:** `pydantic_settings.BaseSettings`

**Параметры:**

**Обязательные:**
- `telegram_bot_token: str` - токен бота
- `openrouter_api_key: str` - API ключ Openrouter

**Опциональные (с дефолтами):**
- `llm_model: str = "openai/gpt-oss-20b:free"`
- `llm_temperature: float = 0.7` (0.0-2.0)
- `llm_max_tokens: int = 1000` (1-100000)
- `llm_timeout: int = 30` (1-300)
- `max_history_messages: int = 10` (1-100)
- `system_prompt_path: str = "prompts/nutritionist.txt"`

**Валидация:**
- Автоматическое приведение типов (str → int/float)
- Constraints через `Field` (min_length, ge, le)
- Pydantic типы (`PositiveInt`, `PositiveFloat`)

---

### `src/protocols.py` - Protocol Interfaces

**Назначение:** Абстракции для Dependency Inversion Principle

**ConversationStorageProtocol:**
```python
def add_message(user_id, chat_id, role, content) -> None
def get_history(user_id, chat_id) -> list[ChatMessage]
def clear_history(user_id, chat_id) -> None
```

**LLMClientProtocol:**
```python
async def get_response(messages: list[ChatMessage]) -> str
```

**Использование:**
- `MessageHandler` зависит от Protocol, а не от конкретных классов
- Легко заменить реализацию
- Упрощает тестирование с моками

---

### `src/types.py` - Type Definitions

**ChatMessage TypedDict:**
```python
class ChatMessage(TypedDict):
    role: str       # "user" | "assistant" | "system"
    content: str    # текст сообщения
```

Совместим с OpenAI API форматом.

## Configuration Files

### `pyproject.toml`

**Секции:**
- `[project]` - метаданные, зависимости
- `[project.optional-dependencies]` - dev зависимости
- `[tool.ruff]` - настройки линтера/форматтера
- `[tool.mypy]` - настройки type checker
- `[tool.pytest.ini_options]` - настройки тестов

**Ключевые настройки:**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
strict = true  # Строгая типизация

[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = ["--cov=src", "--cov-fail-under=70"]
```

---

### `Makefile`

**Доступные команды:**
```makefile
make install      # Установка зависимостей
make run          # Запуск бота
make format       # Форматирование (ruff format)
make lint         # Проверка (ruff check)
make typecheck    # Проверка типов (mypy)
make test         # Запуск тестов
make test-cov     # Тесты с coverage
make quality      # Полная проверка (format + lint + typecheck + test)
make clean        # Очистка временных файлов
```

## Test Structure

```
tests/
├── unit/
│   ├── test_config.py           # Тесты Pydantic валидации
│   ├── test_conversation.py     # Тесты истории диалогов
│   ├── test_llm_client.py       # Тесты LLM клиента (с моками)
│   ├── test_message_handler.py  # Тесты обработчика сообщений
│   └── test_command_handler.py  # Тесты команд
└── conftest.py                   # Общие fixtures
```

**Текущее покрытие:** ~80% (все модули кроме bot.py)

## Prompts Directory

### `prompts/nutritionist.txt`

Системный промпт для роли нутрициолога.

**Как используется:**
1. Загружается при инициализации `LLMClient`
2. Добавляется как system message в начало каждого запроса к LLM
3. Путь настраивается через `SYSTEM_PROMPT_PATH` в `.env`

## Where to Find What?

| Что ищете | Где смотреть |
|-----------|-------------|
| Точка входа | `main.py` |
| Обработка команд | `src/command_handler.py` |
| Обработка сообщений | `src/message_handler.py` |
| LLM интеграция | `src/llm_client.py` |
| История диалогов | `src/conversation.py` |
| Конфигурация | `src/config.py` |
| Типы данных | `src/types.py` |
| Абстракции | `src/protocols.py` |
| Роль бота | `prompts/nutritionist.txt` |
| Тесты | `tests/unit/test_*.py` |
| Команды сборки | `Makefile` |
| Зависимости | `pyproject.toml` |

## File Organization Principles

**1 класс = 1 файл:**
```
bot.py              → TelegramBot
command_handler.py  → CommandHandler
message_handler.py  → MessageHandler
llm_client.py       → LLMClient
conversation.py     → Conversation
config.py           → Config
```

**Именование:**
- Файлы: `snake_case.py`
- Классы: `PascalCase`
- Функции/методы: `snake_case`
- Константы: `UPPER_SNAKE_CASE`

## Next Steps

- ⚙️ [Configuration & Secrets](07_configuration_secrets.md) - детали конфигурации
- 🔨 [Development Workflow](08_development_workflow.md) - как работать с кодом
- 🧪 [Testing Guide](09_testing_guide.md) - как писать тесты

