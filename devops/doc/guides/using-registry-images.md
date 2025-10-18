# Использование образов из GitHub Container Registry

Практическое руководство по работе с Docker образами из GHCR в проекте Systech AIDD.

## Два режима работы

Проект поддерживает два режима запуска Docker контейнеров:

### 1. Локальная сборка (Development)

**Когда использовать:**
- 🔧 Разработка и отладка
- 🐛 Тестирование изменений в коде
- 📝 Изменение Dockerfile
- 🚀 Первый запуск проекта

**Как использовать:**
```bash
# Собрать образы локально
make docker-build

# Запустить сервисы
make docker-up

# Просмотр логов
make docker-logs
```

**Файл:** `docker-compose.yml` (основной)

**Особенности:**
- Собирает образы из исходного кода на вашей машине
- Изменения в коде требуют пересборки (`make docker-build`)
- Не требует интернет после первой установки зависимостей

---

### 2. Образы из Registry (Testing/Production)

**Когда использовать:**
- ✅ Тестирование опубликованных версий
- 🚀 Production deployment
- 🔍 Проверка работы CI/CD
- 📦 Быстрый запуск без локальной сборки

**Как использовать:**
```bash
# Pull образов из GHCR
make docker-pull

# Запустить сервисы
make docker-up-prod

# Просмотр логов
make docker-logs-prod
```

**Файл:** `docker-compose.prod.yml`

**Особенности:**
- Использует готовые образы из GitHub Container Registry
- Не требует локальной сборки (быстрее)
- Всегда актуальная версия из main ветки (тег `latest`)
- Требует интернет для первого pull

## Быстрый старт

### Первый раз: локальная сборка

```bash
# 1. Создать .env файл (если еще нет)
cp .env.example .env
# Отредактировать .env (добавить токены)

# 2. Собрать и запустить
make docker-build
make docker-up

# 3. Проверить работу
make docker-ps
make docker-logs
```

### Использование образов из registry

```bash
# 1. Pull образов
make docker-pull

# 2. Запустить
make docker-up-prod

# 3. Проверить работу
make docker-ps-prod
make docker-logs-prod
```

## Сравнение режимов

| Параметр | Локальная сборка | Registry образы |
|----------|------------------|-----------------|
| **Файл** | `docker-compose.yml` | `docker-compose.prod.yml` |
| **Команда build** | `make docker-build` | `make docker-pull` |
| **Команда up** | `make docker-up` | `make docker-up-prod` |
| **Время первого запуска** | 5-10 минут | 2-3 минуты |
| **Изменения в коде** | Видны после rebuild | Не видны |
| **Интернет** | Нужен для зависимостей | Нужен для pull |
| **Использование** | Development | Testing, Production |

## Детальные команды

### Локальная сборка

```bash
# Полный цикл
make docker-build      # Собрать образы
make docker-up         # Запустить
make docker-logs       # Логи всех сервисов

# Управление
make docker-down       # Остановить
make docker-restart    # Перезапустить
make docker-ps         # Статус контейнеров

# Логи отдельных сервисов
make docker-logs-bot
make docker-logs-api
make docker-logs-frontend

# Очистка
make docker-clean      # Остановить + удалить volumes
```

### Registry образы

```bash
# Полный цикл
make docker-pull       # Pull образов
make docker-up-prod    # Запустить
make docker-logs-prod  # Логи всех сервисов

# Управление
make docker-down-prod     # Остановить
make docker-restart-prod  # Перезапустить
make docker-ps-prod       # Статус контейнеров

# Обновление образов
make docker-pull          # Pull новых версий
make docker-restart-prod  # Перезапуск с новыми образами

# Или одной командой
make docker-down-prod && make docker-pull && make docker-up-prod
```

## Переключение между режимами

### С локальной сборки на registry

```bash
# 1. Остановить локальные контейнеры
make docker-down

# 2. Pull образов из registry
make docker-pull

# 3. Запустить с registry образами
make docker-up-prod
```

### С registry на локальную сборку

```bash
# 1. Остановить prod контейнеры
make docker-down-prod

# 2. Собрать локально
make docker-build

# 3. Запустить локальные контейнеры
make docker-up
```

**💡 Совет:** Контейнеры разных режимов не конфликтуют (разные названия). Можно просто переключаться командами `up`/`down`.

## Работа с конкретными версиями образов

### Использование latest (по умолчанию)

`docker-compose.prod.yml` использует тег `:latest` из main ветки.

```yaml
image: ghcr.io/OWNER/systech-aidd-bot:latest
```

### Использование конкретного коммита

Отредактируйте `docker-compose.prod.yml`:

```yaml
# Вместо latest
image: ghcr.io/OWNER/systech-aidd-bot:latest

# Используйте SHA коммита
image: ghcr.io/OWNER/systech-aidd-bot:sha-abc1234
```

### Использование конкретной ветки

```yaml
image: ghcr.io/OWNER/systech-aidd-bot:branch-develop
```

**Затем:**
```bash
make docker-pull
make docker-up-prod
```

## Обновление образов

### Когда нужно обновлять?

Образы в registry обновляются автоматически при каждом push:
- Push в `main` → обновляется тег `latest`
- Push в любую ветку → создается/обновляется тег `branch-<name>`
- Каждый commit → создается тег `sha-<commit>`

### Как получить обновления локально?

```bash
# 1. Pull новых образов
make docker-pull

# 2. Перезапустить контейнеры
make docker-restart-prod

# Или одной командой (с полным пересозданием)
make docker-down-prod && make docker-pull && make docker-up-prod
```

**💡 Совет:** Docker кэширует слои. Если образ не изменился, pull будет быстрым.

## Сценарии использования

### Сценарий 1: Разработка новой функции

```bash
# Работаем с локальной сборкой
make docker-build
make docker-up

# Вносим изменения в код
# ...

# Пересобираем и перезапускаем
make docker-build
make docker-restart
```

### Сценарий 2: Тестирование PR

```bash
# Переключаемся на ветку PR
git checkout feature/new-feature

# Pull образов из ветки
export GITHUB_REPOSITORY_OWNER=your-username

# Отредактировать docker-compose.prod.yml:
# image: ghcr.io/OWNER/systech-aidd-bot:branch-feature-new-feature

make docker-pull
make docker-up-prod
```

### Сценарий 3: Production deploy на сервер

```bash
# На сервере
cd /opt/systech-aidd

# Pull latest образов
make docker-pull

# Запустить/обновить
make docker-up-prod

# Проверить логи
make docker-logs-prod
```

### Сценарий 4: Откат на предыдущую версию

```bash
# Найти SHA предыдущего рабочего коммита на GitHub
# Например: abc1234

# Отредактировать docker-compose.prod.yml
# image: ghcr.io/OWNER/systech-aidd-bot:sha-abc1234

make docker-pull
make docker-restart-prod
```

## Настройка GITHUB_REPOSITORY_OWNER

`docker-compose.prod.yml` использует переменную `GITHUB_REPOSITORY_OWNER` для определения owner репозитория.

### Вариант 1: Переменная окружения (временно)

```bash
export GITHUB_REPOSITORY_OWNER=your-github-username
make docker-up-prod
```

### Вариант 2: В .env файле (постоянно)

Добавить в `.env`:
```env
GITHUB_REPOSITORY_OWNER=your-github-username
```

### Вариант 3: Отредактировать docker-compose.prod.yml

Заменить:
```yaml
image: ghcr.io/${GITHUB_REPOSITORY_OWNER:-systech}/systech-aidd-bot:latest
```

На:
```yaml
image: ghcr.io/your-github-username/systech-aidd-bot:latest
```

## Troubleshooting

### Проблема: образы не скачиваются

```
Error response from daemon: pull access denied
```

**Решение:**
1. Проверьте, что образы опубликованы: `https://github.com/OWNER?tab=packages`
2. Проверьте, что образы public (или авторизуйтесь: `docker login ghcr.io`)
3. Проверьте правильность GITHUB_REPOSITORY_OWNER

### Проблема: старая версия образа

```bash
# Принудительно скачать новые образы
docker-compose -f docker-compose.prod.yml pull --no-cache

# Или удалить локальные образы
docker images | grep systech-aidd | awk '{print $3}' | xargs docker rmi -f

# Затем pull снова
make docker-pull
```

### Проблема: контейнеры не запускаются

```bash
# Проверить логи
make docker-logs-prod

# Проверить статус
make docker-ps-prod

# Проверить, что .env файл на месте
cat .env
```

### Проблема: конфликт портов

```
Error: port is already allocated
```

**Решение:**
1. Остановите другой режим: `make docker-down` или `make docker-down-prod`
2. Или измените порты в соответствующем docker-compose файле

## Планы на следующие спринты

### Sprint D2: Ручной Deploy

Образы из GHCR будут использоваться для развертывания на удаленный сервер:

```bash
# На сервере
ssh user@server
cd /opt/systech-aidd
git pull
make docker-pull
make docker-up-prod
```

**Документация:** `devops/doc/guides/manual-deploy.md` (будет создана в D2)

### Sprint D3: Auto Deploy

GitHub Actions автоматически развернет новые образы после успешной сборки:

1. Push в `main` → собираются образы → публикуются в GHCR
2. GitHub Actions подключается к серверу по SSH
3. На сервере выполняются команды: `docker-pull`, `docker-up-prod`
4. Проверка работоспособности

**Документация:** `.github/workflows/deploy.yml` (будет создан в D3)

## Лучшие практики

### 1. Development: локальная сборка

```bash
make docker-build
make docker-up
```

### 2. Testing: образы из registry

```bash
make docker-pull
make docker-up-prod
```

### 3. Production: конкретные версии

```yaml
# Не используйте latest в production
image: ghcr.io/owner/app:latest  # ❌

# Используйте конкретный SHA
image: ghcr.io/owner/app:sha-abc1234  # ✅
```

### 4. Регулярные обновления

```bash
# Еженедельно или при необходимости
make docker-pull
make docker-restart-prod
```

### 5. Мониторинг логов

```bash
# Регулярно проверяйте логи
make docker-logs-prod

# Или отдельные сервисы
docker-compose -f docker-compose.prod.yml logs -f bot
```

## Полезные команды

```bash
# Проверка доступных образов в registry
curl -s https://ghcr.io/v2/OWNER/systech-aidd-bot/tags/list | jq

# Проверка локальных образов
docker images | grep systech-aidd

# Информация об образе
docker inspect ghcr.io/OWNER/systech-aidd-bot:latest

# История слоев образа
docker history ghcr.io/OWNER/systech-aidd-bot:latest

# Размер образа
docker images ghcr.io/OWNER/systech-aidd-bot --format "{{.Size}}"

# Удаление неиспользуемых образов
docker image prune -a

# Полная очистка Docker (осторожно!)
docker system prune -a --volumes
```

## Дополнительные ресурсы

- [GitHub Actions Intro](../github-actions-intro.md) - введение в CI/CD
- [GHCR Setup Guide](ghcr-setup.md) - настройка registry
- [Docker Quick Start](../../DOCKER_QUICK_START.md) - быстрый старт с Docker
- [DevOps Roadmap](../devops-roadmap.md) - план развития инфраструктуры

---

**Готово! 🚀 Вы знаете всё о работе с образами из registry!**

