# Решение проблем Docker

Документация по решению типичных проблем при работе с Docker в проекте.

## Frontend: Cannot find module 'react' или 'styled-jsx/package.json'

### Проблема

При сборке frontend контейнера возникает одна из ошибок:
```
Error: Cannot find module 'styled-jsx/package.json'
Error: The module 'react' was not found. Next.js requires that you include it in 'dependencies' of your 'package.json'
```

### Причина

Next.js использует `styled-jsx` и другие модули как встроенные зависимости. При использовании pnpm (вместо npm/yarn) возникает проблема с hoisting зависимостей - pnpm не поднимает вложенные зависимости на верхний уровень `node_modules`, что требуется Next.js.

Дополнительная проблема может быть в двойном копировании `package.json` в Dockerfile, что создает конфликт путей.

### Решение

**1. Создан файл `frontend/.npmrc`:**

```ini
shamefully-hoist=true
public-hoist-pattern[]=*styled-jsx*
```

**Параметры:**
- `shamefully-hoist=true` - включает полный hoisting всех зависимостей (как в npm)
- `public-hoist-pattern[]=*styled-jsx*` - явно поднимает styled-jsx на верхний уровень

**2. Упрощен `devops/Dockerfile.frontend`:**

```dockerfile
FROM node:20-slim

WORKDIR /app

# Установить pnpm
RUN npm install -g pnpm@10.18.3

# Скопировать все файлы frontend (node_modules исключен через .dockerignore)
COPY frontend/ ./

# Установить зависимости с правильной конфигурацией
RUN pnpm install --frozen-lockfile --shamefully-hoist

# Собрать production build
RUN pnpm build

EXPOSE 3000
CMD ["pnpm", "start"]
```

**Ключевые изменения:**
- Копируем все файлы `frontend/` сразу (включая `.npmrc`)
- Используем флаг `--shamefully-hoist` прямо в команде установки
- Нет двойного копирования `package.json`
- `node_modules` автоматически исключен через `.dockerignore`

---

## Frontend: ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY

### Проблема

При сборке frontend контейнера возникает ошибка:
```
ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY
Aborted removal of modules directory due to no TTY
```

### Причина

pnpm обнаружил существующую директорию `node_modules` и пытается запросить подтверждение на её удаление. В Docker нет интерактивного терминала (TTY), поэтому операция прерывается.

Это может произойти если:
1. В Docker build context попала директория `node_modules` (не исключена `.dockerignore`)
2. pnpm нашёл остатки предыдущей установки
3. Кеш Docker содержит слой с `node_modules`

### Решение

**Обновлен `devops/Dockerfile.frontend`:**

```dockerfile
# Скопировать все файлы frontend (node_modules исключен через .dockerignore)
COPY frontend/ ./

# Убедиться что node_modules не существует
RUN rm -rf node_modules

# Установить зависимости с правильной конфигурацией
RUN pnpm install --frozen-lockfile --shamefully-hoist --force
```

**Ключевые изменения:**
- `rm -rf node_modules` - явно удаляем node_modules перед установкой
- `--force` - флаг заставляет pnpm пересоздать node_modules без запроса подтверждения

### Проверка

После исправления пересоберите образ:

```bash
# Очистить кеш Docker для полной пересборки
docker-compose build --no-cache frontend

# Или пересобрать все без кеша
docker-compose build --no-cache

# Проверить успешность сборки
docker images | grep systech-aidd-frontend
```

### Альтернативные решения

Если проблема сохраняется, попробуйте:

**Вариант 1: Использовать npm вместо pnpm**

```dockerfile
FROM node:20-slim

WORKDIR /app

# Скопировать package.json и package-lock.json
COPY frontend/package*.json ./

# Установить зависимости через npm
RUN npm ci --production

# Скопировать исходный код
COPY frontend/. ./

# Собрать production build
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

**Вариант 2: Установить styled-jsx явно**

Добавить в `frontend/package.json`:
```json
{
  "dependencies": {
    "styled-jsx": "5.1.1"
  }
}
```

**Вариант 3: Использовать node_modules linker**

В `frontend/.npmrc`:
```ini
node-linker=hoisted
```

---

## Dashboard: Ошибка подключения к API (ERR_CONNECTION_REFUSED)

### Проблема

При открытии `http://localhost:3000/dashboard` страница показывает "Загрузка данных..." и не загружается. В консоли браузера ошибка:
```
ERR_CONNECTION_REFUSED @ http://localhost:8000/api/stats
```

### Причины

**Причина 1:** API контейнер не запущен или падает с ошибкой

Проверить:
```bash
docker-compose ps api
# Если показывает "Restarting" - контейнер падает

docker logs systech-aidd-api --tail 50
# Посмотреть ошибки
```

**Частая ошибка:** отсутствует `TELEGRAM_BOT_TOKEN` в environment для API:
```
ValidationError: 1 validation error for Config
telegram_bot_token: Field required
```

**Причина 2:** Неправильный `NEXT_PUBLIC_API_URL` в docker-compose.yml

Если в docker-compose установлено:
```yaml
frontend:
  environment:
    NEXT_PUBLIC_API_URL: http://api:8000  # <- НЕ работает из браузера!
```

Браузер пользователя не может обратиться к хосту `api` (это внутренний Docker network адрес).

### Решение

**1. Убедитесь что API контейнер имеет все необходимые переменные:**

```yaml
api:
  environment:
    TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}  # <- Обязательно!
    OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
    DATABASE_URL: postgresql+asyncpg://systech:systech_dev_password@postgres:5432/systech_aidd
```

**2. Уберите NEXT_PUBLIC_API_URL из frontend (если он там есть):**

```yaml
frontend:
  # НЕ устанавливайте NEXT_PUBLIC_API_URL
  # Frontend будет использовать дефолт http://localhost:8000
  ports:
    - "3000:3000"
```

**3. Перезапустите сервисы:**

```bash
# Пересобрать frontend (если меняли NEXT_PUBLIC_API_URL)
docker-compose build --no-cache frontend

# Перезапустить API (если добавляли переменные)
docker-compose up -d api

# Проверить статус
docker-compose ps
```

### Проверка

```bash
# API должен быть Up (не Restarting)
docker-compose ps api

# Логи API не должны содержать ошибок
docker logs systech-aidd-api --tail 20

# Dashboard должен загрузиться
# http://localhost:3000/dashboard
```

**Детальная документация:** см. `devops/DASHBOARD_FIX.md`

---

## PostgreSQL: Connection refused

### Проблема

Bot или API не могут подключиться к PostgreSQL:
```
Error: connection refused
```

### Причина

PostgreSQL еще не готов принимать соединения, или используется неправильный хост.

### Решение

**1. Проверьте DATABASE_URL:**

В `docker-compose.yml` должен использоваться **имя сервиса**, а не localhost:
```yaml
DATABASE_URL: postgresql+asyncpg://systech:systech_dev_password@postgres:5432/systech_aidd
#                                                                  ^^^^^^^^ - имя сервиса, НЕ localhost
```

**2. Убедитесь что используется depends_on с healthcheck:**

```yaml
bot:
  depends_on:
    postgres:
      condition: service_healthy  # <- Важно!
```

**3. Проверьте статус PostgreSQL:**

```bash
make docker-ps
# Должен показывать: systech-aidd-postgres Up (healthy)

# Проверить логи
make docker-logs-postgres
# Должно быть: "database system is ready to accept connections"
```

---

## Docker Desktop не запущен

### Проблема

```
Error: Cannot connect to the Docker daemon
```

### Решение

1. Запустите Docker Desktop
2. Дождитесь полной загрузки (значок в трее должен быть зеленым)
3. Попробуйте снова: `make docker-build`

---

## Порты уже заняты

### Проблема

```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

### Причина

Другой процесс использует порт 8000, 3000 или 5432.

### Решение

**Вариант 1: Остановить конфликтующий процесс**

Windows:
```powershell
# Найти процесс на порту 8000
netstat -ano | findstr :8000

# Завершить процесс (замените PID)
taskkill /PID <PID> /F
```

**Вариант 2: Изменить порт в docker-compose.yml**

```yaml
api:
  ports:
    - "8001:8000"  # Внешний порт 8001 вместо 8000
```

---

## Ошибка сборки образа

### Проблема

```
Error: failed to build
```

### Решение

**1. Очистите Docker кеш:**

```bash
docker system prune -a
# Внимание: удалит все неиспользуемые образы!

# Или мягкая очистка:
docker builder prune
```

**2. Проверьте интернет-соединение:**

Убедитесь что можете скачать base images:
```bash
docker pull python:3.11-slim
docker pull node:20-slim
docker pull postgres:16-alpine
```

**3. Проверьте .dockerignore:**

Убедитесь что не исключаются необходимые файлы.

**4. Пересоберите с выводом:**

```bash
# Без кеша и с детальным выводом
docker-compose build --no-cache --progress=plain
```

---

## .env файл не найден

### Проблема

```
Warning: The "TELEGRAM_BOT_TOKEN" variable is not set
```

### Решение

Создайте файл `.env` в **корне проекта** (не в devops/):

```env
# .env
TELEGRAM_BOT_TOKEN=your_token_here
OPENROUTER_API_KEY=your_key_here

# Опционально
LLM_MODEL=openai/gpt-oss-20b:free
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=30
MAX_HISTORY_MESSAGES=10
```

---

## Проверка конфигурации

Перед запуском проверьте корректность конфигурации:

```bash
# Валидация docker-compose.yml
docker-compose config

# Проверка без запуска
docker-compose up --dry-run
```

---

## Полезные команды для диагностики

```bash
# Логи контейнера
docker logs systech-aidd-frontend
docker logs systech-aidd-api --tail 50
docker logs systech-aidd-bot --follow

# Войти в контейнер
docker exec -it systech-aidd-frontend /bin/sh
docker exec -it systech-aidd-api /bin/sh

# Проверить сеть
docker network inspect systech-aidd_systech-network

# Проверить volumes
docker volume ls | grep systech-aidd
docker volume inspect systech-aidd_postgres_data

# Проверить образы
docker images | grep systech-aidd

# Полная информация о контейнере
docker inspect systech-aidd-frontend
```

---

## Получение помощи

Если проблема не решена:

1. Соберите диагностическую информацию:
```bash
docker-compose ps
docker-compose logs
docker images
docker network ls
```

2. Проверьте документацию:
   - [Docker Quick Start](DOCKER_QUICK_START.md)
   - [Sprint D0 Summary](doc/sprint-D0-summary.md)

3. Проверьте логи конкретного сервиса:
```bash
make docker-logs-<service>
```

