# GitHub Container Registry: Настройка и использование

Руководство по работе с GitHub Container Registry (ghcr.io) для проекта Systech AIDD.

## Что такое GHCR?

**GitHub Container Registry (GHCR)** — это бесплатный Docker registry от GitHub:
- 📦 Хранение Docker образов
- 🌍 Public или private доступ
- 🔗 Интеграция с репозиторием
- 🆓 Бесплатно для public репозиториев

**URL образов:** `ghcr.io/OWNER/IMAGE_NAME:TAG`

**Для нашего проекта:**
```
ghcr.io/OWNER/systech-aidd-bot:latest
ghcr.io/OWNER/systech-aidd-api:latest
ghcr.io/OWNER/systech-aidd-frontend:latest
ghcr.io/OWNER/systech-aidd-postgres:latest
```

## Автоматическая публикация через GitHub Actions

### Настройка в workflow (уже сделано)

В `.github/workflows/build.yml` уже настроена автоматическая публикация:

```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**GITHUB_TOKEN** — автоматически предоставляется GitHub Actions, никакой дополнительной настройки не требуется!

### Что происходит при push

1. **Push в любую ветку** → запускается workflow
2. **Собираются 4 образа** параллельно (bot, api, frontend, postgres)
3. **Образы тегируются:**
   - `sha-<commit>` — для всех коммитов
   - `branch-<name>` — имя ветки
   - `latest` — только для main ветки
4. **Публикуются в GHCR** автоматически

### Проверка публикации

После успешного workflow образы появятся:
- В разделе **Packages** вашего профиля GitHub
- URL: `https://github.com/OWNER?tab=packages`

## Настройка публичного доступа

По умолчанию образы создаются **private** (доступны только владельцу).

### Как сделать образы публичными

Для каждого образа нужно изменить visibility на public:

**Шаг 1:** Найти package
- Откройте `https://github.com/OWNER?tab=packages`
- Найдите образ `systech-aidd-bot`

**Шаг 2:** Открыть Package Settings
- Нажмите на package
- Справа внизу: **Package settings**

**Шаг 3:** Изменить visibility
- Секция **Danger Zone**
- **Change package visibility**
- Выберите **Public**
- Подтвердите действие

**Повторите для всех 4 образов:**
- `systech-aidd-bot`
- `systech-aidd-api`
- `systech-aidd-frontend`
- `systech-aidd-postgres`

### Проверка публичного доступа

После установки public visibility:
- ✅ Образы можно pull без авторизации
- ✅ Видны всем пользователям GitHub
- ✅ Отображаются в публичном профиле

Проверить можно командой (без авторизации):
```bash
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
```

## Локальная авторизация (опционально)

Для private образов или приватных репозиториев нужна авторизация.

### Создание Personal Access Token (PAT)

**Шаг 1:** Создать токен
- Settings → Developer settings → Personal access tokens → Tokens (classic)
- **Generate new token (classic)**

**Шаг 2:** Настроить права
- Имя: `GHCR Access`
- Права:
  - ✅ `read:packages` — pull образов
  - ✅ `write:packages` — push образов (опционально)
  - ✅ `delete:packages` — удаление образов (опционально)

**Шаг 3:** Сохранить токен
- Скопируйте токен (показывается один раз!)

### Авторизация в Docker

```bash
# Вариант 1: интерактивно (вставить PAT как пароль)
docker login ghcr.io -u USERNAME

# Вариант 2: через переменную
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Вариант 3: прямо в команде (не рекомендуется)
docker login ghcr.io -u USERNAME -p TOKEN
```

### Проверка авторизации

```bash
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
```

Если успешно → авторизация работает! 🎉

## Работа с образами

### Pull образов

**Один образ:**
```bash
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
```

**Все образы:**
```bash
make docker-pull
```

Или вручную:
```bash
docker-compose -f docker-compose.prod.yml pull
```

### Указание конкретного тега

```bash
# Последний коммит в main
docker pull ghcr.io/OWNER/systech-aidd-bot:latest

# Конкретный коммит
docker pull ghcr.io/OWNER/systech-aidd-bot:sha-abc1234

# Конкретная ветка
docker pull ghcr.io/OWNER/systech-aidd-bot:branch-develop
```

### Просмотр локальных образов

```bash
docker images | grep systech-aidd
```

### Удаление локальных образов

```bash
# Один образ
docker rmi ghcr.io/OWNER/systech-aidd-bot:latest

# Все образы проекта
docker images | grep systech-aidd | awk '{print $3}' | xargs docker rmi
```

## Использование образов из registry

### Запуск через docker-compose.prod.yml

```bash
# Pull образов
make docker-pull

# Запустить все сервисы
make docker-up-prod

# Проверить статус
make docker-ps-prod

# Просмотр логов
make docker-logs-prod
```

### Переключение между локальной сборкой и registry

**Локальная сборка (разработка):**
```bash
make docker-build    # Собрать образы
make docker-up       # Запустить
```

**Registry образы (testing/production):**
```bash
make docker-pull     # Pull образов
make docker-up-prod  # Запустить
```

### Установка owner репозитория

По умолчанию в `docker-compose.prod.yml` используется переменная `GITHUB_REPOSITORY_OWNER`.

Установить вручную:
```bash
export GITHUB_REPOSITORY_OWNER=your-github-username
make docker-up-prod
```

Или отредактировать `docker-compose.prod.yml`, заменив `${GITHUB_REPOSITORY_OWNER:-systech}` на ваш username.

## Управление образами на GitHub

### Просмотр версий

На странице package можно увидеть:
- Все теги образа
- Размер образа
- Дату публикации
- Связь с коммитом

### Удаление образа/версии

**Package settings** → **Manage versions** → **Delete**

⚠️ **Осторожно:** удаление необратимо!

### Связь с репозиторием

GitHub автоматически связывает package с репозиторием, откуда он опубликован.

На странице package есть ссылка на:
- Репозиторий
- Коммит, в котором собран образ
- Workflow run

## Troubleshooting

### Ошибка: "unauthorized: unauthenticated"

**Проблема:** нет авторизации для pull private образа.

**Решение:**
1. Проверьте, что образ public (см. раздел выше)
2. Или авторизуйтесь через `docker login ghcr.io`

### Ошибка: "Error response from daemon: pull access denied"

**Проблема:** неправильное имя образа или нет прав доступа.

**Решение:**
1. Проверьте правильность имени: `ghcr.io/OWNER/systech-aidd-bot:latest`
2. OWNER должен быть в lowercase
3. Убедитесь что образ существует: `https://github.com/OWNER?tab=packages`

### Ошибка в GitHub Actions: "denied: permission_denied"

**Проблема:** недостаточно прав для публикации образа.

**Решение:**
- Проверьте, что в workflow есть `permissions: packages: write`
- Проверьте, что используется `GITHUB_TOKEN` (не custom PAT)

### Образы не появляются в Packages

**Возможные причины:**
1. Workflow упал с ошибкой — проверьте логи в Actions
2. Push не прошел — проверьте статус в workflow
3. Нет прав на публикацию — проверьте permissions

**Как проверить:**
- Actions tab → выберите workflow run → проверьте каждый job

### Старые образы занимают много места

**Решение:** периодически удаляйте старые версии через Package settings.

**Автоматизация (будущее):**
- Можно настроить GitHub Actions для автоудаления старых образов
- Использовать retention policy (если доступно)

## Лучшие практики

### 1. Используйте public для open source

Если проект публичный — делайте образы public:
- ✅ Упрощает использование
- ✅ Не требует авторизации
- ✅ Бесплатно

### 2. Тегируйте образы правильно

- `latest` — только для main/stable
- `sha-*` — для отслеживания конкретного коммита
- `branch-*` — для тестирования веток

### 3. Проверяйте образы перед использованием

```bash
# Посмотреть информацию об образе
docker inspect ghcr.io/OWNER/systech-aidd-bot:latest

# Проверить слои
docker history ghcr.io/OWNER/systech-aidd-bot:latest
```

### 4. Используйте specific tags в production

```yaml
# ❌ Плохо: latest может измениться
image: ghcr.io/owner/app:latest

# ✅ Хорошо: конкретная версия
image: ghcr.io/owner/app:sha-abc1234
```

### 5. Очищайте старые образы

Периодически удаляйте неиспользуемые версии для экономии места.

## Интеграция с Deployment

### Sprint D2: Ручной Deploy

Образы из GHCR будут использоваться для ручного развертывания на сервер:
```bash
ssh user@server
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Sprint D3: Auto Deploy

GitHub Actions автоматически развернет новые образы на сервер после успешной сборки.

## Полезные команды

```bash
# Просмотр всех образов проекта
docker images | grep systech-aidd

# Pull всех образов
make docker-pull

# Запуск с prod образами
make docker-up-prod

# Логи prod контейнеров
make docker-logs-prod

# Остановка prod контейнеров
make docker-down-prod

# Обновление образов
make docker-pull && make docker-restart-prod

# Полная очистка и перезапуск
make docker-down-prod && make docker-pull && make docker-up-prod
```

## Полезные ссылки

- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [About permissions for GitHub Packages](https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages)
- [Publishing packages](https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions)

---

**Готово! 🚀 GHCR настроен и готов к использованию!**

