# Systech AIDD Bot

AI-ассистент на базе Telegram с интеграцией LLM через Openrouter.

## 🚀 Возможности

- 💬 Общение с AI через Telegram
- 🧠 Использование различных LLM моделей (по умолчанию: GPT-OSS-20B Free)
- 💾 Персистентное хранение истории диалогов в PostgreSQL
- 📝 Сохранение истории диалога (последние 10 сообщений)
- 🔄 Soft delete - данные не удаляются физически
- ⚙️ Управление через команды
- 🛡️ Graceful обработка ошибок

## 📋 Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку по командам
- `/clear` - Очистить историю диалога


## 🔧 Требования

- Python 3.11+
- uv (менеджер пакетов)
- Docker (для PostgreSQL)
- Telegram Bot Token (получить через @BotFather)
- Openrouter API Key (получить на https://openrouter.ai/)

## 🐳 Быстрый старт с Docker (Рекомендуется)

### Запуск всего стека одной командой

1. **Создать .env файл:**
```bash
# Обязательные параметры
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Опциональные (есть значения по умолчанию)
LLM_MODEL=openai/gpt-oss-20b:free
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=30
MAX_HISTORY_MESSAGES=10
```

2. **Запустить все сервисы:**
```bash
docker-compose up -d
```

Готово! 🎉 Все сервисы запущены:
- 🤖 **Telegram Bot** - обрабатывает сообщения
- 🔌 **API** - http://localhost:8000 (документация: http://localhost:8000/docs)
- 🌐 **Frontend** - http://localhost:3000
- 💾 **PostgreSQL** - localhost:5432

### Управление Docker-стеком

```bash
# Запуск
make docker-up                # Запустить все сервисы
make docker-build             # Пересобрать образы
make docker-restart           # Перезапустить сервисы

# Мониторинг
make docker-ps                # Статус контейнеров
make docker-logs              # Логи всех сервисов
make docker-logs-bot          # Логи только бота
make docker-logs-api          # Логи только API
make docker-logs-frontend     # Логи только фронтенда

# Остановка
make docker-down              # Остановить все сервисы
make docker-clean             # Остановить + удалить volumes
```

### Первый запуск

При первом запуске `docker-compose up`:
1. Собираются Docker образы (может занять 2-5 минут)
2. Запускается PostgreSQL
3. Автоматически применяются миграции БД
4. Запускаются Bot, API, Frontend

Логи можно смотреть в реальном времени: `make docker-logs`

---

## 📦 Локальная разработка (без Docker)

Если нужна разработка без Docker, следуйте инструкциям ниже.

### Установка

### 1. Клонировать репозиторий
```bash
git clone <repository-url>
cd systech-aidd
```

### 2. Установить зависимости
```bash
make install
```

Или напрямую через uv:
```bash
uv sync --all-extras
```

### 3. Запустить PostgreSQL

Запустить базу данных через Docker Compose:
```bash
docker-compose up -d
```

Проверить статус:
```bash
docker-compose ps
```

### 4. Настроить переменные окружения

Создайте файл `.env` в корне проекта:
```bash
# Обязательные параметры
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
DATABASE_URL=postgresql+asyncpg://systech:systech_dev_password@localhost:5432/systech_aidd

# Опциональные (есть значения по умолчанию)
LLM_MODEL=openai/gpt-oss-20b:free
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=30
MAX_HISTORY_MESSAGES=10
SYSTEM_PROMPT_PATH=prompts/nutritionist.txt
```

### 5. Применить миграции БД

```bash
uv run alembic upgrade head
```

## 🏃 Запуск

```bash
make run
```

Или напрямую:
```bash
uv run python main.py
```

Бот запустится и начнет обрабатывать сообщения в Telegram.

## 🏗️ Архитектура

```
systech-aidd/
├── src/
│   ├── bot.py                    # Главный класс Telegram бота
│   ├── llm_client.py             # Клиент для работы с Openrouter API
│   ├── message_handler.py        # Обработка сообщений пользователя
│   ├── database_conversation.py  # Хранение истории в PostgreSQL
│   ├── database.py               # Connection pool и утилиты БД
│   └── config.py                 # Конфигурация из .env
├── alembic/                      # Миграции базы данных
├── main.py                       # Точка входа
├── docker-compose.yml            # PostgreSQL окружение
├── pyproject.toml                # Зависимости проекта
├── Makefile                      # Команды для сборки и запуска
└── .env                          # Переменные окружения (не в git)
```

## 🔄 Поток обработки сообщения

1. Пользователь отправляет сообщение в Telegram
2. `TelegramBot` получает сообщение
3. `MessageHandler` получает историю из `DatabaseConversation` (PostgreSQL)
4. `LLMClient` отправляет запрос в Openrouter
5. Ответ сохраняется в `DatabaseConversation` с метаданными
6. Бот отправляет ответ пользователю

## ⚙️ Конфигурация

Все параметры настраиваются через `.env` файл:

| Параметр | Описание | По умолчанию | Обязательный |
|----------|----------|--------------|--------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | - | ✅ |
| `OPENROUTER_API_KEY` | API ключ Openrouter | - | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `LLM_MODEL` | Модель LLM | `openai/gpt-oss-20b:free` | ❌ |
| `LLM_TEMPERATURE` | Температура генерации | `0.7` | ❌ |
| `LLM_MAX_TOKENS` | Максимум токенов | `1000` | ❌ |
| `LLM_TIMEOUT` | Таймаут запроса (сек) | `30` | ❌ |
| `MAX_HISTORY_MESSAGES` | Максимум сообщений в истории | `10` | ❌ |

## 🧪 Тестирование

1. Запустите бота: `make run`
2. Найдите своего бота в Telegram
3. Отправьте `/start` для начала работы
4. Попробуйте различные команды и отправьте текстовые сообщения

### Тестовые сценарии:

**Базовый функционал:**
- Отправьте `/start` - должно прийти приветствие
- Отправьте текстовое сообщение - должен прийти ответ от LLM
- Отправьте `/help` - должна показаться справка

**История диалога:**
- Напишите "Меня зовут Иван"
- Напишите "Как меня зовут?" - бот должен помнить имя
- Отправьте `/clear`
- Напишите "Как меня зовут?" - бот не должен помнить

**Обработка ошибок:**
- Бот продолжает работать при ошибках API
- Пользователь получает понятные сообщения об ошибках

## 🛠️ Разработка

### Работа через UI Cursor/VS Code

Проект настроен для работы через интерфейс Cursor/VS Code. Доступны следующие возможности:

#### 🎯 Запуск и отладка (F5)

В меню "Run and Debug" доступны конфигурации:
- **🤖 Запустить бота** - запуск с отладкой
- **🧪 Запустить все тесты** - запуск всех тестов
- **🧪 Запустить тесты с покрытием** - тесты + coverage report
- **🧪 Запустить текущий тест** - запуск открытого файла
- **🧪 Unit тесты** - только unit тесты
- **🧪 Integration тесты** - только integration тесты

#### ⚙️ Задачи (Terminal > Run Task)

Доступные задачи:
- **🤖 Запустить бота** - запуск бота
- **🧪 Запустить все тесты** - все тесты (Ctrl+Shift+T)
- **🧪 Тесты с покрытием** - тесты + HTML отчет
- **🎨 Форматирование кода** - автоформатирование через ruff
- **🔍 Линтер (проверка)** - проверка стиля кода
- **🔧 Линтер (исправление)** - автоисправление проблем
- **🔬 Проверка типов** - mypy type checking
- **✅ Полная проверка качества** - format + lint + typecheck + test
- **✅ Проверка качества (без тестов)** - для итераций 1-4
- **📦 Установить зависимости** - uv sync
- **🧹 Очистка** - удаление временных файлов

#### 🧪 Testing UI

В панели Testing (колба на боковой панели):
- Автоматическое обнаружение тестов
- Запуск отдельных тестов/групп
- Отладка тестов с брейкпоинтами
- Просмотр результатов в реальном времени

#### 💡 Настройки

Проект автоматически настроен на:
- Форматирование при сохранении (Ruff)
- Автоимпорты и их сортировка
- Линтинг в реальном времени
- Подсветка ошибок типов (MyPy)

### Доступные команды Make:

```bash
# Установка и запуск
make install              # Установить зависимости
make run                  # Запустить бота

# Качество кода
make format               # Форматирование кода (ruff)
make lint                 # Проверка линтером (ruff check)
make lint-fix             # Исправление проблем линтера
make typecheck            # Проверка типов (mypy)

# Тестирование
make test                 # Запуск всех тестов
make test-cov             # Тесты с coverage отчетом

# Комплексные проверки
make quality              # Полная проверка: format + lint + typecheck + test
make quality-no-test      # Без тестов: format + lint + typecheck

# Очистка
make clean                # Очистить временные файлы

# База данных
docker-compose up -d      # Запустить PostgreSQL
docker-compose down       # Остановить PostgreSQL
uv run alembic upgrade head    # Применить миграции
uv run alembic downgrade -1    # Откатить последнюю миграцию
```

### Логирование

Все события логируются в консоль (stdout) в формате:
```
[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE
```

Уровни логирования:
- `INFO` - нормальная работа (команды, сообщения, ответы)
- `ERROR` - ошибки с полным stacktrace

## 🐛 Обработка ошибок

Бот реализует принцип **graceful degradation**:
- При ошибках API бот продолжает работать
- Пользователю показываются понятные сообщения
- Все ошибки логируются с деталями
- Таймаут запросов предотвращает зависание

Типы обрабатываемых ошибок:
- **Timeout** - превышение времени ожидания ответа
- **Authentication** - проблемы с API ключом
- **Rate Limit** - превышение лимита запросов
- **API Error** - общие ошибки API
- **Unexpected** - непредвиденные ошибки

## 📝 Принципы разработки

Проект следует принципу **KISS** (Keep It Simple, Stupid):
- Максимальная простота решений
- 1 класс = 1 файл
- Минимум абстракций
- Явное лучше неявного

## 📚 Документация

**Полная документация проекта:** [docs/README.md](docs/README.md)

### Гайды для разработчиков

- 🚀 [Getting Started](docs/guides/01_getting_started.md) - быстрый старт
- 🎨 [Visual Architecture](docs/guides/02_visual_architecture.md) - **12 типов диаграмм**
- 🏗️ [Architecture Overview](docs/guides/03_architecture_overview.md) - обзор архитектуры
- 🗺️ [Codebase Tour](docs/guides/04_codebase_tour.md) - структура кода
- ⚙️ [Configuration & Secrets](docs/guides/07_configuration_secrets.md) - конфигурация
- 🔨 [Development Workflow](docs/guides/08_development_workflow.md) - разработка
- 🧪 [Testing Guide](docs/guides/09_testing_guide.md) - тестирование
- 💾 [Database Migrations](docs/guides/10_database_migrations.md) - работа с БД и миграциями

### Проектная документация

- [Vision](docs/vision.md) - техническое видение
- [Conventions](docs/conventions.md) - соглашения разработки
- [Review #0001](docs/reviews/review_0001.md) - код-ревью (оценка 9/10)

### Architecture Decision Records (ADR)

- [ADR 0001](docs/adr/0001-postgresql-raw-sql-alembic.md) - выбор PostgreSQL + Raw SQL + Alembic


## 👤 Автор

Systech Team
