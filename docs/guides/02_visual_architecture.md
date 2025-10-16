# Visual Architecture Guide

Визуальное представление архитектуры проекта с разных точек зрения.

---

## 🏗️ High-Level Architecture

**Общая архитектура системы:**

```mermaid
graph TB
    User[👤 User<br/>Telegram Client]
    
    subgraph "Telegram Bot Application"
        Bot[🤖 Bot<br/>aiogram Dispatcher]
        CH[⚙️ Command Handler<br/>/start /help /clear]
        MH[💬 Message Handler<br/>User messages]
        Conv[📚 Conversation<br/>History Manager]
        Config[⚙️ Config<br/>Settings]
    end
    
    subgraph "External Services"
        Telegram[☁️ Telegram API<br/>Bot Platform]
        OpenRouter[🧠 Openrouter API<br/>LLM Service]
    end
    
    subgraph "Storage"
        Memory[(🗂️ In-Memory<br/>Dict Storage)]
        Prompts[(📝 File System<br/>prompts/*.txt)]
    end
    
    User -->|messages| Telegram
    Telegram -->|updates| Bot
    Bot -->|commands| CH
    Bot -->|text| MH
    MH <-->|history| Conv
    Conv <-->|store| Memory
    MH -->|API call| OpenRouter
    MH -->|load| Prompts
    Config -.->|configure| Bot
    Config -.->|configure| MH
    Bot -->|responses| Telegram
    Telegram -->|responses| User
    
    style User fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style Bot fill:#fff9c4,stroke:#f57f17,stroke-width:3px,color:#000
    style CH fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style MH fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style Conv fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Config fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style Telegram fill:#e3f2fd,stroke:#0d47a1,stroke-width:3px,color:#000
    style OpenRouter fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style Memory fill:#f1f8e9,stroke:#33691e,stroke-width:2px,color:#000
    style Prompts fill:#f1f8e9,stroke:#33691e,stroke-width:2px,color:#000
```

---

## 🔄 Message Flow (Sequence Diagram)

**Полный цикл обработки сообщения пользователя:**

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User
    participant TG as ☁️ Telegram API
    participant Bot as 🤖 Bot
    participant MH as 💬 MessageHandler
    participant Conv as 📚 Conversation
    participant LLM as 🧠 LLMClient
    participant OR as 🌐 Openrouter
    
    User->>TG: Send message
    TG->>Bot: Update event
    Bot->>MH: handle_message()
    
    MH->>Conv: get_history(user_id, chat_id)
    Conv-->>MH: List[Message]
    
    MH->>MH: Build messages list
    MH->>LLM: send_message(messages)
    
    LLM->>OR: POST /api/v1/chat/completions
    OR-->>LLM: Response (streaming)
    LLM-->>MH: AI response
    
    MH->>Conv: add_message(user_msg)
    MH->>Conv: add_message(ai_msg)
    
    MH->>Bot: Send response
    Bot->>TG: API call
    TG->>User: Display message
    
    Note over Conv: History kept<br/>last 10 messages
    
    rect rgba(255, 249, 196, 0.3)
    Note right of Bot: Bot Layer
    end
    
    rect rgba(227, 242, 253, 0.3)
    Note right of TG: External Services
    end
```

---

## 🗂️ Component Architecture

**Компоненты и их взаимосвязи:**

```mermaid
graph LR
    subgraph "Entry Point"
        Main[main.py<br/>🚀 Entry Point]
    end
    
    subgraph "Core Components"
        Bot[bot.py<br/>🤖 Bot Orchestrator]
        CH[command_handler.py<br/>⚙️ Command Handler]
        MH[message_handler.py<br/>💬 Message Handler]
    end
    
    subgraph "Business Logic"
        Conv[conversation.py<br/>📚 Conversation Manager]
        LLM[llm_client.py<br/>🧠 LLM Client]
    end
    
    subgraph "Infrastructure"
        Config[config.py<br/>⚙️ Configuration]
        Proto[protocols.py<br/>📋 Protocols]
        Types[types.py<br/>📦 Type Definitions]
    end
    
    Main -->|creates| Bot
    Bot -->|registers| CH
    Bot -->|registers| MH
    MH -->|uses| Conv
    MH -->|uses| LLM
    Bot -->|loads| Config
    MH -->|implements| Proto
    Conv -->|uses| Types
    LLM -->|uses| Types
    
    style Main fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style Bot fill:#fff9c4,stroke:#f57f17,stroke-width:3px,color:#000
    style CH fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style MH fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style Conv fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style LLM fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style Config fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style Proto fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style Types fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
```

---

## 🎯 Class Diagram

**Основные классы и их отношения:**

```mermaid
classDiagram
    class Config {
        +str telegram_bot_token
        +str openrouter_api_key
        +str llm_model
        +float llm_temperature
        +int max_history_messages
        +load_system_prompt(filename) str
    }
    
    class TelegramBot {
        -Bot _bot
        -Dispatcher _dp
        -Config _config
        +create(config) TelegramBot
        +start() None
        +stop() None
    }
    
    class ConversationManager {
        -dict _conversations
        -int _max_messages
        +get_history(user_id, chat_id) list
        +add_message(user_id, chat_id, message) None
        +clear_history(user_id, chat_id) None
    }
    
    class LLMClient {
        -str _api_key
        -str _model
        -float _temperature
        -int _timeout
        +send_message(messages) str
        -_build_headers() dict
        -_build_payload(messages) dict
    }
    
    class CommandHandler {
        -ConversationProtocol _conversation
        +cmd_start(message) None
        +cmd_help(message) None
        +cmd_clear(message) None
        +cmd_new(message) None
        +cmd_role(message, role) None
    }
    
    class MessageHandler {
        -LLMClientProtocol _llm_client
        -ConversationProtocol _conversation
        -str _system_prompt
        +handle_message(message) None
    }
    
    class ConversationProtocol {
        <<interface>>
        +get_history(user_id, chat_id)*
        +add_message(user_id, chat_id, message)*
        +clear_history(user_id, chat_id)*
    }
    
    class LLMClientProtocol {
        <<interface>>
        +send_message(messages)*
    }
    
    TelegramBot --> Config
    TelegramBot --> CommandHandler
    TelegramBot --> MessageHandler
    MessageHandler --> LLMClientProtocol
    MessageHandler --> ConversationProtocol
    CommandHandler --> ConversationProtocol
    LLMClient ..|> LLMClientProtocol
    ConversationManager ..|> ConversationProtocol
    
    style Config fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style TelegramBot fill:#fff9c4,stroke:#f57f17,stroke-width:3px,color:#000
    style ConversationManager fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style LLMClient fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style CommandHandler fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style MessageHandler fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style ConversationProtocol fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style LLMClientProtocol fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
```

---

## 📊 Data Flow Diagram

**Потоки данных в системе:**

```mermaid
graph LR
    subgraph Input
        UserMsg[👤 User Message]
        EnvVars[⚙️ .env Variables]
        SysPrompt[📝 System Prompt]
    end
    
    subgraph Processing
        Parse[Parse Message]
        LoadHist[Load History]
        BuildCtx[Build Context]
        CallLLM[Call LLM API]
        SaveHist[Save to History]
    end
    
    subgraph Storage
        MemStore[(In-Memory Dict)]
    end
    
    subgraph Output
        Response[🤖 Bot Response]
    end
    
    UserMsg -->|text| Parse
    Parse -->|user_id, chat_id| LoadHist
    LoadHist <-->|read| MemStore
    EnvVars -->|config| CallLLM
    SysPrompt -->|role| BuildCtx
    LoadHist -->|messages| BuildCtx
    BuildCtx -->|context| CallLLM
    CallLLM -->|AI answer| SaveHist
    SaveHist -->|write| MemStore
    SaveHist -->|response| Response
    
    style UserMsg fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style Response fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px,color:#000
    style MemStore fill:#f1f8e9,stroke:#33691e,stroke-width:3px,color:#000
    style Parse fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style LoadHist fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style BuildCtx fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style CallLLM fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style SaveHist fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style EnvVars fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style SysPrompt fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
```

---

## 🔁 Conversation State Machine

**Состояния диалога:**

```mermaid
stateDiagram-v2
    [*] --> NoHistory: First message
    
    NoHistory --> Active: User sends message
    Active --> Active: Continue conversation
    Active --> Cleared: /clear or /new command
    Cleared --> Active: New message
    Active --> RoleChanged: /role command
    RoleChanged --> Active: Continue with new role
    
    Active --> HistoryFull: 10+ messages
    HistoryFull --> HistoryFull: Auto-trim oldest
    HistoryFull --> Cleared: /clear or /new
    
    state Active {
        [*] --> WaitingUser
        WaitingUser --> ProcessingLLM: Message received
        ProcessingLLM --> SavingHistory: LLM responded
        SavingHistory --> WaitingUser: Saved
    }
    
    note right of NoHistory
        Empty conversation
        No context
    end note
    
    note right of Active
        Conversation in progress
        History: 1-10 messages
    end note
    
    note right of HistoryFull
        Auto-trim to last 10
        FIFO queue
    end note
    
    note right of Cleared
        History deleted
        Fresh start
    end note
```

---

## 🚀 Deployment View

**Как развернута и запущена система:**

```mermaid
graph TB
    subgraph "Local/Server Environment"
        EnvFile[.env file<br/>🔐 Secrets]
        PyProject[pyproject.toml<br/>📦 Dependencies]
        MainPy[main.py<br/>🚀 Entry point]
        SrcCode[src/<br/>💻 Source code]
        Prompts[prompts/<br/>📝 Prompt files]
        
        subgraph "Runtime"
            Python[Python 3.11+<br/>🐍 Interpreter]
            UvEnv[uv Environment<br/>📦 Virtual env]
            Process[Bot Process<br/>⚡ Running]
        end
    end
    
    subgraph "External Services"
        TelegramCloud[Telegram Bot API<br/>☁️ telegram.org]
        OpenRouterCloud[Openrouter API<br/>🧠 openrouter.ai]
    end
    
    EnvFile -.->|load secrets| Process
    PyProject -->|install deps| UvEnv
    MainPy -->|execute| Python
    Python -->|use env| UvEnv
    Python -->|run| Process
    SrcCode -->|import| Process
    Prompts -->|read| Process
    
    Process <-->|Long polling| TelegramCloud
    Process -->|HTTP API| OpenRouterCloud
    
    style EnvFile fill:#fce4ec,stroke:#880e4f,stroke-width:3px,color:#000
    style Process fill:#ff6b6b,stroke:#c92a2a,stroke-width:4px,color:#fff
    style TelegramCloud fill:#e3f2fd,stroke:#0d47a1,stroke-width:3px,color:#000
    style OpenRouterCloud fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style Python fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style UvEnv fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style MainPy fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style SrcCode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style Prompts fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style PyProject fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
```

---

## 👤 User Journey

**Путь пользователя от старта до диалога:**

```mermaid
journey
    title User Interaction Flow
    section Getting Started
      Find bot in Telegram: 5: User
      Send /start: 5: User
      Read welcome message: 4: User
    section First Conversation
      Ask nutrition question: 5: User
      Wait for AI response: 3: User, Bot
      Receive expert advice: 5: User
    section Ongoing Dialog
      Continue conversation: 5: User
      Get contextual responses: 5: User, Bot
      History preserved (10 msg): 4: Bot
    section Managing History
      Send /clear command: 4: User
      Confirm cleared: 4: Bot
      Start fresh dialog: 5: User
    section Change Role
      Send /role fitness: 4: User
      Bot changes to fitness trainer: 5: Bot
      Get fitness advice: 5: User
```

---

## 🧩 Module Dependencies

**Зависимости между модулями:**

```mermaid
graph TD
    main[main.py] --> bot
    bot[bot.py] --> config
    bot --> cmd_handler[command_handler.py]
    bot --> msg_handler[message_handler.py]
    
    cmd_handler --> protocols
    cmd_handler --> conversation
    
    msg_handler --> protocols
    msg_handler --> llm_client[llm_client.py]
    msg_handler --> conversation[conversation.py]
    msg_handler --> config
    
    llm_client --> config
    llm_client --> types[types.py]
    
    conversation --> types
    
    protocols[protocols.py] -.->|defines| conversation
    protocols -.->|defines| llm_client
    
    style main fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style bot fill:#fff9c4,stroke:#f57f17,stroke-width:3px,color:#000
    style config fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style cmd_handler fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style msg_handler fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style llm_client fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style conversation fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style protocols fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style types fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
```

---

## 🔧 Configuration Flow

**Как загружается и используется конфигурация:**

```mermaid
flowchart TD
    Start([🚀 Application Start]) --> LoadEnv[Load .env file]
    LoadEnv --> CreateConfig[Create Config instance]
    CreateConfig --> Validate{Pydantic<br/>Validation}
    
    Validate -->|❌ Error| ShowError[Show validation error]
    ShowError --> Exit([❌ Exit])
    
    Validate -->|✅ Success| ConfigReady[Config Ready]
    
    ConfigReady --> CreateBot[Create TelegramBot]
    ConfigReady --> CreateLLM[Create LLMClient]
    ConfigReady --> CreateConv[Create ConversationManager]
    
    CreateBot --> UseToken[Use telegram_bot_token]
    CreateLLM --> UseAPI[Use openrouter_api_key<br/>+ llm settings]
    CreateConv --> UseMax[Use max_history_messages]
    
    UseToken --> BotReady[🤖 Bot Ready]
    UseAPI --> LLMReady[🧠 LLM Ready]
    UseMax --> ConvReady[📚 Conversation Ready]
    
    BotReady --> Running([✅ Application Running])
    LLMReady --> Running
    ConvReady --> Running
    
    style Start fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style Running fill:#c8e6c9,stroke:#2e7d32,stroke-width:4px,color:#000
    style Exit fill:#ffcdd2,stroke:#c62828,stroke-width:3px,color:#000
    style Validate fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style ConfigReady fill:#fce4ec,stroke:#880e4f,stroke-width:3px,color:#000
    style BotReady fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style LLMReady fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style ConvReady fill:#f1f8e9,stroke:#33691e,stroke-width:2px,color:#000
```

---

## 📦 Technology Stack

**Технологический стек проекта:**

```mermaid
mindmap
  root((Systech AIDD Bot))
    Core
      Python 3.11+
      Asyncio
      Type Hints
    Bot Framework
      aiogram 3.15+
      Telegram Bot API
    LLM Integration
      Openrouter API
      aiohttp client
      Streaming support
    Configuration
      pydantic 2.10+
      pydantic-settings
      python-dotenv
    Development
      ruff formatter
      ruff linter
      mypy strict
      pytest
      pytest-asyncio
      pytest-cov
    Packaging
      uv package manager
      pyproject.toml
```

---

## 🎨 Design Patterns Used

**Применяемые паттерны проектирования:**

```mermaid
graph TB
    subgraph "Structural Patterns"
        Facade[🎭 Facade<br/>TelegramBot class<br/>Hides aiogram complexity]
        DI[💉 Dependency Injection<br/>Protocols injected<br/>into handlers]
    end
    
    subgraph "Behavioral Patterns"
        Strategy[🎯 Strategy<br/>Different role prompts<br/>Change behavior]
        Observer[👁️ Observer<br/>aiogram handlers<br/>React to events]
    end
    
    subgraph "Creational Patterns"
        Factory[🏭 Factory Method<br/>TelegramBot.create()<br/>Bot initialization]
        Singleton[👑 Singleton-like<br/>Single config instance<br/>Global settings]
    end
    
    subgraph "SOLID Principles"
        SRP[S: Single Responsibility<br/>Each class = 1 purpose]
        OCP[O: Open/Closed<br/>Protocol extensions]
        LSP[L: Liskov Substitution<br/>Protocol implementations]
        ISP[I: Interface Segregation<br/>Small focused protocols]
        DIP[D: Dependency Inversion<br/>Depend on protocols]
    end
    
    Facade -.->|enables| SRP
    DI -.->|implements| DIP
    Strategy -.->|supports| OCP
    Observer -.->|follows| OCP
    
    style Facade fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
    style DI fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style Strategy fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Observer fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style Factory fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Singleton fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style SRP fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    style OCP fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    style LSP fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    style ISP fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    style DIP fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
```

---

## 🔍 Quick Visual Reference

| Диаграмма | Что показывает | Когда использовать |
|-----------|----------------|-------------------|
| **High-Level Architecture** | Общая структура системы | Объяснить архитектуру новичку |
| **Message Flow** | Последовательность обработки | Понять порядок вызовов |
| **Component Architecture** | Зависимости модулей | Найти нужный компонент |
| **Class Diagram** | Классы и их связи | Понять ООП структуру |
| **Data Flow** | Потоки данных | Проследить данные |
| **State Machine** | Состояния диалога | Понять lifecycle |
| **Deployment** | Окружение запуска | Развернуть проект |
| **User Journey** | UX флоу | Понять пользователя |
| **Module Dependencies** | Импорты модулей | Рефакторинг |
| **Configuration Flow** | Загрузка настроек | Debug конфигурации |
| **Tech Stack** | Используемые технологии | Онбординг разработчика |
| **Design Patterns** | Паттерны проектирования | Понять архитектурные решения |

---

## 📖 Navigation

- [← Back to Guides](README.md)
- [Getting Started →](01_getting_started.md)
- [Architecture Overview →](03_architecture_overview.md)


