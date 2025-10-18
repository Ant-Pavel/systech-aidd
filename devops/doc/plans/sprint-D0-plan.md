# План спринта D0: Basic Docker Setup

## Статус: ✅ Выполнен

## Цель

Запустить все 4 сервиса (PostgreSQL, Bot, API, Frontend) локально через `docker-compose up` одной командой.

## Обзор изменений

### Созданные файлы

- ✅ `devops/Dockerfile.postgres` - образ для PostgreSQL
- ✅ `devops/Dockerfile.bot` - образ для Telegram бота (Python + UV)
- ✅ `devops/Dockerfile.api` - образ для FastAPI API (Python + UV)
- ✅ `devops/Dockerfile.frontend` - образ для Next.js frontend (Node.js + pnpm)
- ✅ `.dockerignore` - исключение ненужных файлов при сборке

### Обновленные файлы

- ✅ `docker-compose.yml` - добавлены bot, api, frontend сервисы и общая сеть
- ✅ `Makefile` - добавлены команды для управления Docker-стеком
- ✅ `README.md` - добавлены инструкции по запуску через Docker

## Реализованные компоненты

### 1. Dockerfile для PostgreSQL

**Файл:** `devops/Dockerfile.postgres`

Простой Dockerfile на базе `postgres:16-alpine` с метаданными и настройками для будущего расширения.

**Ключевые особенности:**
- Alpine Linux для меньшего размера
- UTF8 encoding по умолчанию
- Готов к добавлению init scripts

### 2. Dockerfile для Bot сервиса

**Файл:** `devops/Dockerfile.bot`

Python 3.11 контейнер с UV менеджером пакетов.

**Ключевые особенности:**
- Автоматическое применение миграций БД при старте
- Production зависимости (`--no-dev`)
- Включает alembic для миграций

### 3. Dockerfile для API сервиса

**Файл:** `devops/Dockerfile.api`

FastAPI сервис на Python 3.11.

**Ключевые особенности:**
- Порт 8000 для FastAPI
- Без alembic (миграции выполняет bot)
- Uvicorn внутри api_main.py

### 4. Dockerfile для Frontend сервиса

**Файл:** `devops/Dockerfile.frontend`

Next.js приложение на Node.js 20.

**Ключевые особенности:**
- pnpm 10.18.3 менеджер пакетов
- Production build
- Порт 3000 (стандартный для Next.js)

### 5. .dockerignore

Общий файл для исключения ненужных файлов из Docker context:
- Python cache и virtual environments
- Node.js modules и build artifacts
- Git, IDE конфигурации
- Документация и тесты
- .env файлы

### 6. docker-compose.yml

**Изменения:**

1. **PostgreSQL:**
   - Заменен `image: postgres:16-alpine` на `build` с Dockerfile
   - Добавлена сеть `systech-network`

2. **Bot сервис (новый):**
   - Зависит от PostgreSQL с healthcheck
   - Автоматически применяет миграции при старте
   - Переменные окружения из .env
   - Restart policy: unless-stopped

3. **API сервис (новый):**
   - Зависит от PostgreSQL с healthcheck
   - Порт 8000 открыт наружу
   - Переменные окружения из .env
   - Restart policy: unless-stopped

4. **Frontend сервис (новый):**
   - Зависит от API
   - Порт 3000 открыт наружу
   - API_URL: http://api:8000 (через Docker network)
   - Restart policy: unless-stopped

5. **Общая сеть:**
   - `systech-network` bridge network для всех сервисов

### 7. Makefile - Docker команды

Добавлены удобные команды:

**Управление:**
- `make docker-build` - собрать все образы
- `make docker-up` - запустить все сервисы в фоне
- `make docker-down` - остановить все сервисы
- `make docker-restart` - перезапустить сервисы

**Мониторинг:**
- `make docker-ps` - статус контейнеров
- `make docker-logs` - логи всех сервисов
- `make docker-logs-bot` - логи только бота
- `make docker-logs-api` - логи только API
- `make docker-logs-frontend` - логи только фронтенда

**Очистка:**
- `make docker-clean` - остановить + удалить volumes и unused images

### 8. README.md

Добавлена новая секция "🐳 Быстрый старт с Docker":

1. **Инструкция по созданию .env файла**
2. **Команда запуска:** `docker-compose up -d`
3. **Список запущенных сервисов** с портами
4. **Управление Docker-стеком** - все make команды
5. **Процесс первого запуска** - что происходит внутри

Старая секция переименована в "📦 Локальная разработка (без Docker)"

## Результат

✅ **Успешно реализовано:**

- ✅ Все 4 Dockerfile созданы в директории `devops/`
- ✅ `.dockerignore` оптимизирует сборку образов
- ✅ `docker-compose.yml` управляет всеми 4 сервисами
- ✅ Общая сеть `systech-network` для межсервисного взаимодействия
- ✅ Автоматическое применение миграций БД при старте bot
- ✅ Healthcheck для PostgreSQL с зависимостями
- ✅ Удобные make команды для управления
- ✅ Полная документация в README.md

## Тестирование

Для проверки работоспособности:

```bash
# 1. Создать .env файл с токенами
# 2. Собрать образы
make docker-build

# 3. Запустить все сервисы
make docker-up

# 4. Проверить статус
make docker-ps

# 5. Посмотреть логи
make docker-logs

# 6. Проверить работу:
# - Telegram Bot - отправить сообщение боту
# - API - открыть http://localhost:8000/docs
# - Frontend - открыть http://localhost:3000
```

## MVP Ограничения

Следующие улучшения **НЕ включены** в MVP (будут в следующих спринтах):

- ❌ Multi-stage builds (оптимизация размера образов)
- ❌ Volume маппинг для hot-reload разработки
- ❌ Healthcheck для API и Frontend
- ❌ Оптимизация слоев Docker образов
- ❌ Автоматическое создание .env файла

**Это осознанные компромиссы MVP подхода!**

## Следующие шаги

Спринт D0 завершен. Готовы к:

- **Спринт D1:** Build & Publish - автоматическая сборка и публикация образов в GitHub Container Registry
- Обновление статуса в `devops/doc/devops-roadmap.md`

