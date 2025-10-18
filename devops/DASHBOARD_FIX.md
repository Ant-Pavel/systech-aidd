# Исправление Dashboard - ошибка подключения к API

## Проблема

При открытии http://localhost:3000/dashboard возникали ошибки:

1. **Frontend**: `ERR_CONNECTION_REFUSED @ http://localhost:8000/api/stats?period=7d`
2. **API**: постоянный перезапуск контейнера с ошибкой `telegram_bot_token Field required`

## Диагностика

### Шаг 1: Проверка frontend

```bash
# Открыли dashboard в браузере
http://localhost:3000/dashboard

# Результат: "Загрузка данных..." не исчезает
# Console error: ERR_CONNECTION_REFUSED @ http://localhost:8000
```

### Шаг 2: Проверка статуса контейнеров

```bash
docker-compose ps

# Результат:
# systech-aidd-api     Restarting (1)    <- API падает!
# systech-aidd-bot     Up
# systech-aidd-frontend Up
# systech-aidd-postgres Up (healthy)
```

### Шаг 3: Проверка логов API

```bash
docker logs systech-aidd-api --tail 50

# Ошибка:
# pydantic_core._pydantic_core.ValidationError: 1 validation error for Config
# telegram_bot_token
#   Field required
```

## Корневые причины

### Проблема 1: Неправильный NEXT_PUBLIC_API_URL

**Было в `docker-compose.yml`:**
```yaml
frontend:
  environment:
    NEXT_PUBLIC_API_URL: http://api:8000  # <- Не работает из браузера!
```

**Почему не работало:**
- `NEXT_PUBLIC_API_URL` используется в клиентском JavaScript (браузер пользователя)
- Браузер пытается обратиться к хосту `api`, который не существует вне Docker сети
- `http://api:8000` доступен только внутри Docker сети между контейнерами

**Решение:**
- Убрать `NEXT_PUBLIC_API_URL` из docker-compose.yml
- Frontend будет использовать дефолтное значение `http://localhost:8000` из кода
- `localhost:8000` доступен из браузера пользователя

### Проблема 2: Отсутствующий TELEGRAM_BOT_TOKEN для API

**Было в `docker-compose.yml`:**
```yaml
api:
  environment:
    OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
    DATABASE_URL: ...
    # TELEGRAM_BOT_TOKEN отсутствовал!
```

**Почему падало:**
- API использует класс `Config` который требует `TELEGRAM_BOT_TOKEN`
- Переменная не была передана в контейнер
- Pydantic validation падал с ошибкой

**Решение:**
- Добавить `TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}` в environment для API

## Решение

### Изменение 1: Убрать NEXT_PUBLIC_API_URL

**Файл:** `docker-compose.yml`

```yaml
frontend:
  build:
    context: .
    dockerfile: devops/Dockerfile.frontend
  container_name: systech-aidd-frontend
  # NEXT_PUBLIC_API_URL не устанавливаем - будет использоваться дефолт http://localhost:8000
  # Это необходимо потому что браузер пользователя делает запросы, а не контейнер
  ports:
    - "3000:3000"
  depends_on:
    - api
  networks:
    - systech-network
  restart: unless-stopped
```

### Изменение 2: Добавить TELEGRAM_BOT_TOKEN для API

**Файл:** `docker-compose.yml`

```yaml
api:
  build:
    context: .
    dockerfile: devops/Dockerfile.api
  container_name: systech-aidd-api
  environment:
    TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}  # <- ДОБАВЛЕНО
    OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
    DATABASE_URL: postgresql+asyncpg://systech:systech_dev_password@postgres:5432/systech_aidd
    # ... остальные переменные
```

## Применение исправлений

```bash
# 1. Пересобрать frontend без кеша (NEXT_PUBLIC_ встраиваются на build time)
docker-compose build --no-cache frontend

# 2. Перезапустить API с новыми переменными окружения
docker-compose up -d api

# 3. Проверить статус всех сервисов
docker-compose ps

# Ожидаемый результат:
# systech-aidd-api     Up    <- Должен быть Up, не Restarting!
# systech-aidd-frontend Up
```

## Проверка работы

### Шаг 1: Проверить статус контейнеров

```bash
docker-compose ps

# Все контейнеры должны быть Up:
# NAME                  STATUS
# systech-aidd-api      Up
# systech-aidd-bot      Up  
# systech-aidd-frontend Up
# systech-aidd-postgres Up (healthy)
```

### Шаг 2: Проверить логи API

```bash
docker logs systech-aidd-api --tail 20

# Ожидаемый вывод (без ошибок):
# [INFO] Initializing database connection...
# [INFO] Database connection initialized successfully
# [INFO] API documentation available at: http://localhost:8000/docs
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Шаг 3: Открыть Dashboard

```
http://localhost:3000/dashboard
```

**Ожидаемый результат:** ✅

- Страница загружается полностью (нет "Загрузка данных...")
- Показываются метрики:
  - Total Messages
  - Active Conversations  
  - Avg Conversation Length
- График "Messages Over Time" отображается корректно
- Нет ошибок в консоли браузера

## Результат

✅ **Dashboard работает корректно!**

![Dashboard Working](doc/dashboard-working.png)

## Почему возникли эти проблемы?

### 1. Непонимание Next.js NEXT_PUBLIC_ переменных

**NEXT_PUBLIC_** переменные:
- Встраиваются в JavaScript код **на этапе сборки** (build time)
- Выполняются **в браузере клиента**, а не на сервере
- Должны содержать URL доступные из браузера пользователя

**Правило:** 
- Для client-side запросов используйте публичные URL (`http://localhost:8000`, `https://api.example.com`)
- Для server-side запросов можно использовать Docker network URLs (`http://api:8000`)

### 2. Неполная конфигурация docker-compose

API контейнер использует тот же `Config` класс что и Bot, но в docker-compose для API отсутствовал `TELEGRAM_BOT_TOKEN`.

**Урок:** Проверяйте все обязательные переменные окружения для каждого сервиса.

## Файлы изменены

1. ✅ `docker-compose.yml`:
   - Убран `NEXT_PUBLIC_API_URL` из frontend
   - Добавлен `TELEGRAM_BOT_TOKEN` для API

2. ✅ `devops/DASHBOARD_FIX.md` - эта документация

## Команды для быстрой проверки

```bash
# Полная пересборка и перезапуск
docker-compose build --no-cache frontend
docker-compose up -d

# Проверка статуса
docker-compose ps

# Проверка логов
docker-compose logs -f api

# Открыть Dashboard
# http://localhost:3000/dashboard
```

## Важные заметки

### Next.js и Docker

При работе с Next.js в Docker важно понимать:

1. **Server-Side Rendering (SSR)**:
   - Выполняется в контейнере frontend
   - Может использовать Docker network URLs (`http://api:8000`)

2. **Client-Side JavaScript**:
   - Выполняется в браузере пользователя
   - Требует публичные URL (`http://localhost:8000`, `https://...`)

3. **NEXT_PUBLIC_ переменные**:
   - Для client-side кода
   - Встраиваются на build time
   - Требуют rebuild при изменении

### Production deployment

Для production потребуется:
```yaml
frontend:
  environment:
    NEXT_PUBLIC_API_URL: https://api.example.com  # Публичный URL
```

Но для локального Docker это не нужно - достаточно `http://localhost:8000`.

---

**Проблема решена!** Dashboard работает корректно ✅

