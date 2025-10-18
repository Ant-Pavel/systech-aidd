# Docker Quick Start Guide

Краткая справка по запуску проекта через Docker.

## Быстрый старт (3 команды)

```bash
# 1. Убедитесь что .env файл создан
# 2. Собрать образы
make docker-build

# 3. Запустить все сервисы
make docker-up
```

Готово! Все сервисы работают:
- 🤖 Bot - в Telegram
- 🔌 API - http://localhost:8000/docs
- 🌐 Frontend - http://localhost:3000
- 💾 PostgreSQL - localhost:5432

## Основные команды

### Управление

```bash
make docker-build      # Собрать/пересобрать образы
make docker-up         # Запустить все сервисы (-d в фоне)
make docker-down       # Остановить все сервисы
make docker-restart    # Перезапустить сервисы
```

### Мониторинг

```bash
make docker-ps         # Статус всех контейнеров
make docker-logs       # Логи всех сервисов (Ctrl+C для выхода)
make docker-logs-bot   # Логи только бота
make docker-logs-api   # Логи только API
make docker-logs-frontend  # Логи только frontend
```

### Очистка

```bash
make docker-down       # Остановить (данные сохранятся)
make docker-clean      # Остановить + удалить volumes (ВСЕ ДАННЫЕ!)
```

## Требования

1. **Docker Desktop** установлен и запущен
2. **Файл .env** создан в корне проекта:

```env
# .env
TELEGRAM_BOT_TOKEN=your_token_here
OPENROUTER_API_KEY=your_key_here

# Опционально (есть значения по умолчанию)
LLM_MODEL=openai/gpt-oss-20b:free
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=30
MAX_HISTORY_MESSAGES=10
```

## Что происходит при запуске?

```
1. PostgreSQL стартует
   ↓ (ждет healthcheck)
2. Bot стартует
   ↓ (применяет миграции БД)
   ↓ (подключается к Telegram)
3. API стартует
   ↓ (подключается к PostgreSQL)
4. Frontend стартует
   ↓ (подключается к API)

✅ Все работает!
```

## Проверка работоспособности

### 1. Статус контейнеров

```bash
make docker-ps
```

Должно быть:
```
NAME                      STATUS
systech-aidd-postgres     Up (healthy)
systech-aidd-bot          Up
systech-aidd-api          Up
systech-aidd-frontend     Up
```

### 2. Проверка логов

```bash
make docker-logs
```

Ищите:
- ✅ PostgreSQL: "database system is ready"
- ✅ Bot: "Starting Telegram bot..."
- ✅ API: "Uvicorn running on http://0.0.0.0:8000"
- ✅ Frontend: "ready - started server"

### 3. Функциональная проверка

- **Bot:** Отправьте `/start` в Telegram → должен ответить
- **API:** Откройте http://localhost:8000/docs → должен открыться Swagger
- **Frontend:** Откройте http://localhost:3000 → должна загрузиться страница

## Типичные проблемы

### Docker Desktop не запущен

```
Error: Cannot connect to the Docker daemon
```

**Решение:** Запустите Docker Desktop

### Порты заняты

```
Error: port is already allocated
```

**Решение:** 
- Остановите другие сервисы на портах 5432, 8000, 3000
- Или измените порты в `docker-compose.yml`

### .env файл не найден

```
Warning: The "TELEGRAM_BOT_TOKEN" variable is not set
```

**Решение:** Создайте файл `.env` в корне проекта (см. раздел Требования)

### Ошибка сборки образа

```
Error: failed to build
```

**Решение:**
1. Проверьте интернет-соединение
2. Очистите кеш: `docker system prune -a`
3. Попробуйте снова: `make docker-build`

## Полезные команды Docker

```bash
# Просмотр образов
docker images | grep systech-aidd

# Просмотр сетей
docker network ls | grep systech

# Просмотр volumes
docker volume ls | grep systech-aidd

# Войти в контейнер
docker exec -it systech-aidd-bot /bin/sh
docker exec -it systech-aidd-api /bin/sh
docker exec -it systech-aidd-frontend /bin/sh
docker exec -it systech-aidd-postgres psql -U systech -d systech_aidd

# Просмотр логов (без follow)
docker logs systech-aidd-bot
docker logs systech-aidd-api --tail 100
```

## Разработка

### Пересборка после изменений

```bash
# Если изменили код Python (bot/api)
make docker-build
make docker-restart

# Если изменили код Frontend
make docker-build
make docker-restart

# Если изменили Dockerfile
make docker-build
make docker-up
```

### Hot reload не работает

Это ожидаемо для MVP! Образы собираются как production.

Для разработки с hot-reload используйте локальный запуск:
```bash
# Terminal 1: PostgreSQL
docker-compose up -d postgres

# Terminal 2: Bot
make run

# Terminal 3: API  
make api-run

# Terminal 4: Frontend
cd frontend && pnpm dev
```

## Дополнительная информация

- [Детальный план спринта D0](doc/plans/sprint-D0-plan.md)
- [Отчет о выполнении D0](doc/sprint-D0-summary.md)
- [DevOps Roadmap](doc/devops-roadmap.md)
- [Основной README](../README.md)

---

**Готово! 🚀 Проект запущен в Docker!**

