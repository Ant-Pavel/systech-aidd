# Getting Started

Быстрый старт проекта за 5 минут.

## Prerequisites

- **Python 3.11+**
- **uv** - менеджер пакетов ([установка](https://docs.astral.sh/uv/))
- **Docker** - для запуска PostgreSQL ([установка](https://docs.docker.com/get-docker/))
- **Telegram Bot Token** - получить через [@BotFather](https://t.me/botfather)
- **Openrouter API Key** - получить на [openrouter.ai](https://openrouter.ai/)

## Установка

### 1. Клонировать репозиторий

```bash
git clone <repository-url>
cd systech-aidd
```

### 2. Установить зависимости

```bash
make install
```

Или напрямую:
```bash
uv sync --all-extras
```

### 3. Запустить PostgreSQL

Запустить базу данных через Docker Compose:

```bash
docker-compose up -d
```

Проверить, что контейнер запущен:
```bash
docker-compose ps
```

### 4. Настроить переменные окружения

Создать файл `.env` в корне проекта:

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

### 5. Применить миграции базы данных

```bash
uv run alembic upgrade head
```

Вы увидите:
```
INFO  [alembic.runtime.migration] Running upgrade  -> e65a515f830d, create_messages_table
```

## Запуск

```bash
make run
```

Или напрямую:
```bash
uv run python main.py
```

Вы увидите:
```
[2025-10-16 12:00:00] [INFO] [bot] - Bot started successfully
```

## Проверка работоспособности

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Отправьте текстовое сообщение
4. Получите ответ от бота

## Troubleshooting

### Ошибка: Missing TELEGRAM_BOT_TOKEN

**Причина:** Не указан токен бота в `.env`

**Решение:** Убедитесь, что `.env` файл содержит `TELEGRAM_BOT_TOKEN=...`

### Ошибка: Failed to connect to database

**Причина:** PostgreSQL не запущен или неверный DATABASE_URL

**Решение:** 
1. Проверьте что Docker запущен: `docker ps`
2. Запустите PostgreSQL: `docker-compose up -d`
3. Проверьте DATABASE_URL в `.env`

### Ошибка: Authentication error

**Причина:** Неверный API ключ Openrouter

**Решение:** Проверьте `OPENROUTER_API_KEY` в `.env`

### Ошибка: System prompt file not found

**Причина:** Не найден файл `prompts/nutritionist.txt`

**Решение:** Убедитесь, что файл существует или измените `SYSTEM_PROMPT_PATH`

## Что дальше?

- 📖 [Architecture Overview](03_architecture_overview.md) - понять архитектуру
- 🗺️ [Codebase Tour](04_codebase_tour.md) - изучить структуру кода
- ⚙️ [Configuration & Secrets](07_configuration_secrets.md) - настройки в деталях
- 🔨 [Development Workflow](08_development_workflow.md) - начать разработку

