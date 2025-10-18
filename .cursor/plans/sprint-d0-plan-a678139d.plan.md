<!-- a678139d-25f7-498a-8c2c-e09a26d5d260 d77ad84d-d3d3-40b6-a323-63109fac5037 -->
# План спринта D0: Basic Docker Setup

## Цель

Запустить все 4 сервиса (PostgreSQL, Bot, API, Frontend) локально через `docker-compose up` одной командой.

## Обзор изменений

### Новые файлы

- `devops/Dockerfile.postgres` - образ для PostgreSQL
- `devops/Dockerfile.bot` - образ для Telegram бота (Python + UV)
- `devops/Dockerfile.api` - образ для FastAPI API (Python + UV)
- `devops/Dockerfile.frontend` - образ для Next.js frontend (Node.js + pnpm)
- `.dockerignore` - исключение ненужных файлов при сборке

### Обновляемые файлы

- `docker-compose.yml` - добавление bot, api, frontend сервисов и общей сети
- `Makefile` - команды для управления Docker-стеком
- `README.md` - инструкции по запуску через Docker

## Детальный план реализации

### 1. Создать Dockerfile для PostgreSQL

**Файл:** `devops/Dockerfile.postgres`

```dockerfile
FROM postgres:16-alpine

# Метаданные
LABEL maintainer="Systech Team"
LABEL description="PostgreSQL database for Systech AIDD"

# Настройки PostgreSQL (можно расширить в будущем)
ENV POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=C"
```

**Особенности:**

- Базируется на официальном образе `postgres:16-alpine`
- Минималистичный Dockerfile для MVP
- Готов к расширению (init scripts, custom config) в будущих спринтах
- Alpine Linux для меньшего размера образа

**Почему создаем Dockerfile:**

- Единообразие - все сервисы имеют свои Dockerfile в `devops/`
- Готовность к кастомизации (init scripts, extensions, настройки)
- Контроль версионирования конфигурации БД
- Возможность добавить метаданные и labels

**Изменения в `docker-compose.yml`:**

```yaml
postgres:
  build:
    context: .
    dockerfile: devops/Dockerfile.postgres
  container_name: systech-aidd-postgres
  environment:
    POSTGRES_DB: systech_aidd
    POSTGRES_USER: systech
    POSTGRES_PASSWORD: systech_dev_password
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U systech -d systech_aidd"]
    interval: 10s
    timeout: 5s
    retries: 5
  networks:
    - systech-network
```

**Ключевые изменения:**

- Заменить `image: postgres:16-alpine` на `build` с указанием Dockerfile
- Добавить `networks: - systech-network`

---

### 2. Создать Dockerfile для Bot сервиса

**Файл:** `devops/Dockerfile.bot`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установить UV
RUN pip install --no-cache-dir uv

# Скопировать файлы зависимостей
COPY pyproject.toml ./

# Установить зависимости
RUN uv sync --no-dev

# Скопировать исходный код
COPY src/ ./src/
COPY main.py ./
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY prompts/ ./prompts/

# Запуск бота с автоматическим применением миграций
CMD uv run alembic upgrade head && uv run python main.py
```

**Особенности:**

- Python 3.11 (из `pyproject.toml`)
- UV для управления зависимостями
- Автоматическое применение миграций при старте
- Только production зависимости (`--no-dev`)

---

### 3. Создать Dockerfile для API сервиса

**Файл:** `devops/Dockerfile.api`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установить UV
RUN pip install --no-cache-dir uv

# Скопировать файлы зависимостей
COPY pyproject.toml ./

# Установить зависимости
RUN uv sync --no-dev

# Скопировать исходный код
COPY src/ ./src/
COPY api_main.py ./
COPY prompts/ ./prompts/

# Открыть порт
EXPOSE 8000

# Запуск API сервера
CMD ["uv", "run", "python", "api_main.py"]
```

**Особенности:**

- Аналогичен bot, но без alembic (миграции делает bot)
- Порт 8000 для FastAPI
- Запуск через uvicorn (внутри `api_main.py`)

---

### 3. Создать Dockerfile для Frontend сервиса

**Файл:** `devops/Dockerfile.frontend`

```dockerfile
FROM node:20-slim

WORKDIR /app

# Установить pnpm
RUN npm install -g pnpm@10.18.3

# Скопировать package.json и pnpm-lock.yaml
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Установить зависимости
RUN pnpm install --frozen-lockfile

# Скопировать исходный код
COPY frontend/ ./

# Собрать production build
RUN pnpm build

# Открыть порт
EXPOSE 3000

# Запуск Next.js в production режиме
CMD ["pnpm", "start"]
```

**Особенности:**

- Node.js 20 (LTS)
- pnpm версии 10.18.3 (из `frontend/package.json`)
- Production build
- Порт 3000 (стандартный для Next.js)

---

### 4. Создать .dockerignore

**Файл:** `.dockerignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
ENV/
.mypy_cache/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
*.egg-info/

# Node.js / Frontend
node_modules/
.next/
out/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
.pnpm-store/

# Git
.git/
.gitignore
.gitattributes

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Docker
Dockerfile*
docker-compose*.yml
.dockerignore

# Documentation
docs/
*.md
README*

# Tests
tests/
*.test.js
*.test.ts
*.spec.js
*.spec.ts

# Env files (will be provided via docker-compose)
.env
.env.*

# Database
*.db
*.sqlite
postgres_data/
```

**Назначение:** ускорить сборку образов, исключив ненужные файлы

---

### 5. Обновить docker-compose.yml

**Файл:** `docker-compose.yml`

Добавить 3 новых сервиса к существующему postgres:

```yaml
services:
  postgres:
    # ... существующая конфигурация ...
    networks:
         - systech-network

  bot:
    build:
      context: .
      dockerfile: devops/Dockerfile.bot
    container_name: systech-aidd-bot
    environment:
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
      DATABASE_URL: postgresql+asyncpg://systech:systech_dev_password@postgres:5432/systech_aidd
      LLM_MODEL: ${LLM_MODEL:-openai/gpt-oss-20b:free}
      LLM_TEMPERATURE: ${LLM_TEMPERATURE:-0.7}
      LLM_MAX_TOKENS: ${LLM_MAX_TOKENS:-1000}
      LLM_TIMEOUT: ${LLM_TIMEOUT:-30}
      MAX_HISTORY_MESSAGES: ${MAX_HISTORY_MESSAGES:-10}
      SYSTEM_PROMPT_PATH: prompts/nutritionist.txt
    depends_on:
      postgres:
        condition: service_healthy
    networks:
         - systech-network
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: devops/Dockerfile.api
    container_name: systech-aidd-api
    environment:
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
      DATABASE_URL: postgresql+asyncpg://systech:systech_dev_password@postgres:5432/systech_aidd
      LLM_MODEL: ${LLM_MODEL:-openai/gpt-oss-20b:free}
      LLM_TEMPERATURE: ${LLM_TEMPERATURE:-0.7}
      LLM_MAX_TOKENS: ${LLM_MAX_TOKENS:-1000}
      LLM_TIMEOUT: ${LLM_TIMEOUT:-30}
      MAX_HISTORY_MESSAGES: ${MAX_HISTORY_MESSAGES:-10}
      SYSTEM_PROMPT_PATH: prompts/nutritionist.txt
    ports:
         - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
         - systech-network
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: devops/Dockerfile.frontend
    container_name: systech-aidd-frontend
    environment:
      NEXT_PUBLIC_API_URL: http://api:8000
    ports:
         - "3000:3000"
    depends_on:
         - api
    networks:
         - systech-network
    restart: unless-stopped

networks:
  systech-network:
    driver: bridge

volumes:
  postgres_data:
```

**Ключевые моменты:**

- Общая сеть `systech-network` для всех сервисов
- Bot зависит от postgres с проверкой healthcheck
- API зависит от postgres с проверкой healthcheck
- Frontend зависит от API (но без healthcheck для MVP)
- DATABASE_URL использует имя сервиса `postgres` вместо `localhost`
- `restart: unless-stopped` для автоматического перезапуска

---

### 6. Добавить Docker команды в Makefile

**Файл:** `Makefile`

Добавить новый раздел:

```makefile
# Docker команды
.PHONY: docker-build docker-up docker-down docker-restart docker-logs docker-logs-bot docker-logs-api docker-logs-frontend docker-ps docker-clean

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-restart:
	docker-compose restart

docker-logs:
	docker-compose logs -f

docker-logs-bot:
	docker-compose logs -f bot

docker-logs-api:
	docker-compose logs -f api

docker-logs-frontend:
	docker-compose logs -f frontend

docker-ps:
	docker-compose ps

docker-clean:
	docker-compose down -v
	docker system prune -f
```

**Команды:**

- `make docker-build` - собрать все образы
- `make docker-up` - запустить все сервисы в фоне
- `make docker-down` - остановить все сервисы
- `make docker-restart` - перезапустить сервисы
- `make docker-logs` - показать логи всех сервисов
- `make docker-logs-bot/api/frontend` - логи конкретного сервиса
- `make docker-ps` - статус контейнеров
- `make docker-clean` - полная очистка (volumes + unused images)

---

### 7. Обновить README.md

**Файл:** `README.md`

Добавить новую секцию после "🔧 Требования":

````markdown
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
````

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

### 1. Клонировать репозиторий

...

```

**Изменения:**

- Добавлен раздел "🐳 Быстрый старт с Docker" в начало
- Секция "📦 Локальная разработка" для тех, кто хочет без Docker
- Упоминание всех новых make команд
- Простые и понятные инструкции для новичков

---

## Порядок выполнения

1. Создать `.dockerignore` (общий для всех сервисов)
2. Создать `devops/Dockerfile.bot`
3. Создать `devops/Dockerfile.api`
4. Создать `devops/Dockerfile.frontend`
5. Обновить `docker-compose.yml` (добавить bot, api, frontend)
6. Обновить `Makefile` (добавить docker-* команды)
7. Обновить `README.md` (добавить секцию Docker)
8. Тестирование:

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - `make docker-build` - сборка образов
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - `make docker-up` - запуск стека
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - `make docker-ps` - проверка статуса
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - `make docker-logs` - проверка логов
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Проверить работу бота в Telegram
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Открыть http://localhost:3000 - проверить frontend
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Открыть http://localhost:8000/docs - проверить API

## Проверка результата

✅ **Успешное выполнение спринта:**

- Команда `docker-compose up` запускает все 4 сервиса
- PostgreSQL инициализируется с healthcheck
- Миграции применяются автоматически
- Bot подключается к Telegram и отвечает на сообщения
- API доступен на http://localhost:8000 с документацией
- Frontend доступен на http://localhost:3000 и может обращаться к API
- Логи показывают корректную работу всех сервисов
- Команды `make docker-*` работают корректно

## Известные ограничения MVP

- Без multi-stage builds (образы не оптимизированы по размеру)
- Без volume маппинга для hot-reload (rebuild при изменениях)
- Без healthcheck для API и Frontend (только для PostgreSQL)
- Образы не оптимизированы по слоям
- .env файл нужно создавать вручную

**Эти ограничения приемлемы для MVP и будут улучшены в следующих спринтах!**

### To-dos

- [ ] Создать .dockerignore для исключения ненужных файлов
- [ ] Создать devops/Dockerfile.bot для Telegram бота (Python + UV + миграции)
- [ ] Создать devops/Dockerfile.api для FastAPI API (Python + UV)
- [ ] Создать devops/Dockerfile.frontend для Next.js frontend (Node.js + pnpm)
- [ ] Обновить docker-compose.yml - добавить bot, api, frontend сервисы с network
- [ ] Добавить Docker команды в Makefile (build, up, down, logs, ps, clean)
- [ ] Обновить README.md - добавить секцию Docker с инструкциями
- [ ] Протестировать весь Docker стек - сборка, запуск, проверка работы всех сервисов