# Соглашения по разработке Systech AIDD Bot

## 🎯 Основные принципы

### SOLID Principles

#### Single Responsibility Principle (SRP)
- **Один класс = одна ответственность = один файл**
- `TelegramBot` - только координация Bot/Dispatcher и регистрация обработчиков
- `CommandHandler` - только обработка команд (/start, /help, /clear)
- `MessageHandler` - только обработка текстовых сообщений
- `LLMClient` - только взаимодействие с LLM API
- `Conversation` - только управление историей диалогов
- `Config` - только загрузка и валидация конфигурации

#### Dependency Inversion Principle (DIP)
- **Зависимости через Protocol интерфейсы**
- `ConversationStorageProtocol` - абстракция для работы с историей
- `LLMClientProtocol` - абстракция для работы с LLM
- Классы зависят от абстракций, а не от конкретных реализаций
- Легко заменить реализацию (например, с in-memory на БД)

### Организация кода

- **1 класс = 1 файл**
- **Именование файлов**: snake_case (bot.py, message_handler.py)
- **Именование классов**: PascalCase (TelegramBot, MessageHandler)
- **Именование функций/методов**: snake_case (handle_message, get_response)
- **Константы**: UPPER_SNAKE_CASE (MAX_HISTORY_MESSAGES)

## 📋 Type Safety

### Type Hints

- **Обязательны везде**: все функции, методы, переменные класса
- **Строгая типизация**: mypy strict mode
- **Явные типы возврата**: всегда указывать `-> Type` или `-> None`
- **Protocol для интерфейсов**: вместо ABC или наследования

### Примеры

```python
# ✅ Хорошо
def add_message(self, user_id: int, chat_id: int, role: str, content: str) -> None:
    ...

async def get_response(self, messages: list[ChatMessage]) -> str:
    ...

# ❌ Плохо
def add_message(self, user_id, chat_id, role, content):
    ...
```

### TypedDict для структур данных

```python
from typing import TypedDict

class ChatMessage(TypedDict):
    role: str
    content: str
```

## 🧪 Тестирование

### Структура тестов

- **Unit-тесты**: `tests/unit/test_<module>.py`
- **Integration-тесты**: `tests/integration/test_<feature>.py`
- **Fixtures**: `tests/conftest.py`

### Покрытие

- **Минимум 70% coverage** для всего проекта
- Тестируем все публичные методы
- Моки для внешних зависимостей (API, Protocol)

### Async тесты

```python
import pytest

@pytest.mark.asyncio
async def test_handle_message():
    ...
```

## 📦 Зависимости

### Инъекция зависимостей

- **Явная инъекция через конструктор**
- **Зависимости через Protocol интерфейсы**

```python
# ✅ Хорошо
class MessageHandler:
    def __init__(
        self,
        llm_client: LLMClientProtocol,
        conversation: ConversationStorageProtocol
    ) -> None:
        self.llm_client = llm_client
        self.conversation = conversation
```

### Инициализация в main.py

```python
# Порядок создания объектов
config = Config()
llm_client = LLMClient(...)
conversation = Conversation(...)
command_handler = CommandHandler(conversation)
message_handler = MessageHandler(llm_client, conversation)
bot = TelegramBot(token, command_handler, message_handler)
```

## 🎨 Форматирование и линтинг

### Ruff

- **Line length**: 100 символов
- **Target version**: Python 3.11+
- **Автоформатирование**: `make format` перед коммитом
- **Линтинг**: `make lint` для проверки

### Правила

- Игнорируем RUF001, RUF002 (кириллица в строках и docstring)
- Используем все стандартные правила ruff (E, F, I, N, UP, B, C4, SIM, RUF)

## 📝 Документация

### Docstrings

- **На русском языке**
- **Формат**: простые строки, без сложных форматов (не Google, не NumPy style)
- **Для классов**: краткое описание ответственности
- **Для методов**: краткое описание действия

```python
class MessageHandler:
    """Обработка текстовых сообщений от пользователя."""

    async def handle_message(self, user_id: int, chat_id: int, text: str) -> str:
        """Обработать входящее сообщение и вернуть ответ от LLM."""
        ...
```

### Комментарии

- **Минимум комментариев** - код должен быть самодокументируемым
- Комментарии только для сложной логики
- **На русском языке**

## 🔧 Конфигурация

### Pydantic Settings v2

- **BaseSettings** для Config класса
- **Валидация полей** через Field с constraints (min_length, ge, le)
- **Pydantic типы**: PositiveInt, PositiveFloat вместо int/float
- **Автозагрузка** из .env файла через model_config
- **Значения по умолчанию** для опциональных параметров
- **Понятные ошибки**: ValidationError при невалидных данных

```python
from pydantic import Field, PositiveFloat, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    """Конфигурация приложения."""
    
    # Обязательные параметры
    telegram_bot_token: str = Field(
        ..., min_length=1, description="Telegram Bot API token"
    )
    
    # Опциональные с валидацией
    llm_temperature: PositiveFloat = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature"
    )
    llm_max_tokens: PositiveInt = Field(
        default=1000, ge=1, le=100000, description="Max tokens"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
```

### Преимущества Pydantic Config

- ✅ Автоматическое приведение типов (str → int/float)
- ✅ Валидация на уровне типов (PositiveInt > 0)
- ✅ Валидация constraints (ge, le, min_length)
- ✅ Понятные сообщения об ошибках
- ✅ Type-safe с mypy через плагин pydantic.mypy
- ✅ Не нужно вручную вызывать load_dotenv()
- ✅ Case-insensitive загрузка переменных

## 📊 Логирование

### Стандартный logging

- **Уровень INFO** для обычных событий
- **Уровень ERROR** для ошибок
- **Формат**: `[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE`

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Received message from user {user_id}")
logger.error(f"LLM API error: {e}", exc_info=True)
```

## 🚀 Workflow

### Перед коммитом

```bash
make format          # Автоформатирование
make lint            # Проверка линтером
make typecheck       # Проверка типов
make test            # Запуск тестов (когда добавлены)
make quality         # Полная проверка
```

### Коммиты

- **На русском языке**
- **Формат**: `<тип>: <описание>`
- **Типы**: feat, fix, refactor, test, docs, chore, style

```
refactor: добавлены Protocol интерфейсы для DIP
test: добавлены unit-тесты для MessageHandler
docs: обновлена архитектурная документация
```

## ⚠️ Что избегать

### Антипаттерны

- ❌ Множество классов в одном файле
- ❌ Божественные объекты (God objects) - классы с множеством ответственностей
- ❌ Конкретные зависимости вместо абстракций
- ❌ Отсутствие type hints
- ❌ Игнорирование ошибок линтера/mypy

### Оверинжиниринг

- ❌ Не создавать абстракции "на будущее"
- ❌ Не добавлять фичи, которые не нужны сейчас
- ❌ Не усложнять архитектуру без необходимости

## ✅ Чеклист код-ревью

- [ ] Type hints везде
- [ ] Один класс = один файл
- [ ] Классы с одной ответственностью (SRP)
- [ ] Зависимости через Protocol (DIP)
- [ ] Docstrings на русском
- [ ] Логирование важных событий
- [ ] `make quality` проходит без ошибок
- [ ] Тесты написаны и проходят (когда применимо)
- [ ] Документация обновлена

