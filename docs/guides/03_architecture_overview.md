# Architecture Overview

Обзор архитектуры Systech AIDD Bot.

## High-Level Architecture

```mermaid
graph TB
    User[👤 User<br/>Telegram] -->|message| Bot[🤖 TelegramBot<br/>aiogram]
    Bot -->|command| CH[⚙️ CommandHandler]
    Bot -->|text message| MH[💬 MessageHandler]
    MH -->|get history| Conv[📚 Conversation<br/>in-memory]
    MH -->|send request| LLM[🧠 LLMClient<br/>Openrouter]
    LLM -->|response| MH
    MH -->|save| Conv
    MH -->|response| Bot
    Bot -->|answer| User
    
    Config[⚙️ Config<br/>Pydantic] -.->|settings| Bot
    Config -.->|settings| LLM
    Config -.->|settings| Conv
    
    style User fill:#e1f5ff,stroke:#01579b,color:#000
    style Bot fill:#fff9c4,stroke:#f57f17,color:#000
    style CH fill:#f3e5f5,stroke:#4a148c,color:#000
    style MH fill:#f3e5f5,stroke:#4a148c,color:#000
    style Conv fill:#e8f5e9,stroke:#1b5e20,color:#000
    style LLM fill:#ffe0b2,stroke:#e65100,color:#000
    style Config fill:#e0f7fa,stroke:#006064,color:#000
```

## Component Responsibilities

### TelegramBot (`bot.py`)
- Инициализация aiogram Bot и Dispatcher
- Регистрация обработчиков команд и сообщений
- Управление polling режимом
- Отображение индикатора "печатает..."

### CommandHandler (`command_handler.py`)
Обработка команд бота:
- `/start` - приветствие
- `/help` - справка
- `/clear` или `/new` - очистка истории
- `/role` - описание роли нутрициолога

### MessageHandler (`message_handler.py`)
Обработка текстовых сообщений:
- Получение истории диалога
- Формирование запроса к LLM
- Сохранение диалога в историю

### LLMClient (`llm_client.py`)
Интеграция с Openrouter API:
- Загрузка системного промпта из файла
- Отправка запросов к LLM
- Обработка ошибок (timeout, auth, rate limit)

### Conversation (`conversation.py`)
Хранение истории диалогов:
- In-memory storage (dict)
- Ключ: (user_id, chat_id)
- Лимит: последние 10 сообщений

### Config (`config.py`)
Конфигурация через Pydantic:
- Загрузка из `.env`
- Валидация параметров
- Значения по умолчанию

## Message Flow

Полный путь сообщения от пользователя до ответа:

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant B as 🤖 Bot
    participant MH as 💬 MessageHandler
    participant C as 📚 Conversation
    participant L as 🧠 LLMClient
    participant O as ☁️ Openrouter
    
    U->>B: текстовое сообщение
    B->>B: показать "печатает..."
    B->>MH: handle_message(user_id, chat_id, text)
    MH->>C: get_history(user_id, chat_id)
    C-->>MH: history (0-10 messages)
    MH->>MH: добавить текущее сообщение
    MH->>L: get_response(messages)
    L->>L: добавить system prompt
    L->>O: chat.completions.create()
    O-->>L: response
    L-->>MH: answer text
    MH->>C: add_message(user, text)
    MH->>C: add_message(assistant, answer)
    MH-->>B: response
    B->>U: ответ бота
    
    box rgba(255, 235, 238, 0.3) Telegram
    U
    end
    box rgba(232, 245, 233, 0.3) Backend
    B
    MH
    C
    L
    end
    box rgba(255, 243, 224, 0.3) External API
    O
    end
```

## SOLID Principles

### Single Responsibility Principle (SRP)
Каждый класс имеет одну ответственность:
- `TelegramBot` - только координация
- `CommandHandler` - только команды
- `MessageHandler` - только сообщения
- `LLMClient` - только LLM API
- `Conversation` - только история
- `Config` - только конфигурация

### Dependency Inversion Principle (DIP)

Использование Protocol интерфейсов для абстракции:

```mermaid
graph TB
    MH[MessageHandler] -.->|uses| LLP[LLMClientProtocol]
    MH -.->|uses| CSP[ConversationStorageProtocol]
    
    LLP -.->|implemented by| LLC[LLMClient]
    CSP -.->|implemented by| Conv[Conversation]
    
    style MH fill:#f3e5f5,stroke:#4a148c,color:#000
    style LLP fill:#fff9c4,stroke:#f57f17,color:#000
    style CSP fill:#fff9c4,stroke:#f57f17,color:#000
    style LLC fill:#e8f5e9,stroke:#1b5e20,color:#000
    style Conv fill:#e8f5e9,stroke:#1b5e20,color:#000
```

**Преимущества:**
- Легко заменить реализацию (например, Conversation → PostgreSQL)
- Простое тестирование с моками
- Слабая связанность компонентов

## Data Model

```mermaid
graph LR
    CM[ChatMessage<br/>TypedDict]
    CM --> R[role: str<br/>user / assistant / system]
    CM --> C[content: str<br/>текст сообщения]
    
    Conv[Conversation<br/>conversations: dict] --> Key[key: tuple<br/>user_id, chat_id]
    Key --> List[value: list<br/>ChatMessage]
    
    style CM fill:#e1f5ff,stroke:#01579b,color:#000
    style R fill:#fff9c4,stroke:#f57f17,color:#000
    style C fill:#fff9c4,stroke:#f57f17,color:#000
    style Conv fill:#e8f5e9,stroke:#1b5e20,color:#000
    style Key fill:#f3e5f5,stroke:#4a148c,color:#000
    style List fill:#ffe0b2,stroke:#e65100,color:#000
```

**ChatMessage:**
```python
{
    "role": "user",           # user / assistant / system
    "content": "текст сообщения"
}
```

**Conversation storage:**
```python
{
    (user_id, chat_id): [
        {"role": "user", "content": "привет"},
        {"role": "assistant", "content": "Здравствуйте!"},
        ...  # максимум 10 сообщений
    ]
}
```

## Tech Stack

- **Python 3.11+** - язык программирования
- **aiogram 3.x** - Telegram Bot API (polling)
- **openai SDK** - клиент для Openrouter API
- **pydantic 2.x** - валидация конфигурации

**Dev tools:**
- **ruff** - форматтер + линтер
- **mypy** - type checker (strict mode)
- **pytest** - тестирование

## Design Patterns

### Dependency Injection
Явная инъекция через конструктор:
```python
llm_client = LLMClient(...)
conversation = Conversation(...)
message_handler = MessageHandler(llm_client, conversation)
```

### Protocol (Strategy)
Абстракции через `typing.Protocol` вместо наследования

### TypedDict
Структуры данных без классов

## Error Handling

Graceful degradation - бот продолжает работать при ошибках:

```mermaid
graph LR
    E[Exception] --> T{Type?}
    T -->|Timeout| M1[Сообщение:<br/>превышено время]
    T -->|Auth| M2[Сообщение:<br/>проверьте API ключ]
    T -->|RateLimit| M3[Сообщение:<br/>попробуйте позже]
    T -->|Other| M4[Сообщие:<br/>общая ошибка]
    
    M1 --> Log[Logging<br/>+ stacktrace]
    M2 --> Log
    M3 --> Log
    M4 --> Log
    
    Log --> U[Пользователь<br/>получает понятное<br/>сообщение]
    
    style E fill:#ffcdd2,stroke:#c62828,color:#000
    style T fill:#fff9c4,stroke:#f57f17,color:#000
    style M1 fill:#f3e5f5,stroke:#4a148c,color:#000
    style M2 fill:#f3e5f5,stroke:#4a148c,color:#000
    style M3 fill:#f3e5f5,stroke:#4a148c,color:#000
    style M4 fill:#f3e5f5,stroke:#4a148c,color:#000
    style Log fill:#e0f7fa,stroke:#006064,color:#000
    style U fill:#e8f5e9,stroke:#1b5e20,color:#000
```

## Limitations

**Текущие ограничения системы:**
- История диалогов хранится в памяти (пропадает при перезапуске)
- Максимум 10 сообщений в истории
- Polling режим (не webhooks)
- Нет персистентности
- Нет мониторинга

## Next Steps

- 🗺️ [Codebase Tour](04_codebase_tour.md) - детальный обзор файлов
- ⚙️ [Configuration & Secrets](07_configuration_secrets.md) - настройка конфигурации
- 🧪 [Testing Guide](09_testing_guide.md) - как тестируется код

