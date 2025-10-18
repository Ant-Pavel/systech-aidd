<!-- a6b74fac-45c2-4983-a2e1-db6fb712a250 be2703de-c8b3-4dae-97ff-3345a07d2645 -->
# План Sprint D1: Build & Publish

## Цель

Автоматическая сборка и публикация Docker образов в GitHub Container Registry (ghcr.io) при каждом push в репозиторий.

## Контекст

- В Sprint D0 созданы Dockerfile для bot, api, frontend, postgres
- Образы собираются локально через `docker-compose build`
- Теперь добавляем CI/CD для автоматической сборки и публикации

## Основные файлы для изменения

- Создать `.github/workflows/build.yml` - GitHub Actions workflow
- Создать `docker-compose.prod.yml` - для использования образов из registry
- Создать `devops/doc/github-actions-intro.md` - документация по GitHub Actions
- Обновить `README.md` - добавить badges и инструкции
- Обновить `Makefile` - команды для работы с prod-образами
- Создать `devops/doc/guides/ghcr-setup.md` - настройка GHCR

## Шаги реализации

### 1. Документация GitHub Actions (intro)

**Файл:** `devops/doc/github-actions-intro.md`

Создать краткую вводную документацию:

- Что такое GitHub Actions и workflow
- Как работают triggers (on: push, pull_request, workflow_dispatch)
- Принципы работы с Pull Request
- Matrix strategy для параллельной сборки
- Публикация в GitHub Container Registry (public/private)
- Примеры использования secrets

### 2. GitHub Actions Workflow

**Файл:** `.github/workflows/build.yml`

Создать workflow с характеристиками:

- **Trigger:** `on: push` для всех веток
- **Matrix strategy:** параллельная сборка 4 образов (bot, api, frontend, postgres)
- **Кэширование:** Docker layer cache для ускорения
- **Тегирование:**
  - `latest` - только для main ветки
  - `sha-<commit>` - для всех коммитов
  - `branch-<name>` - имя ветки
- **Публикация:** в ghcr.io с public доступом
- **Авторизация:** через `GITHUB_TOKEN` (автоматический)

Формат образов: `ghcr.io/OWNER/systech-aidd-bot:latest`

### 3. Docker Compose для Production

**Файл:** `docker-compose.prod.yml`

Создать версию docker-compose для использования образов из registry:

- Использовать `image:` вместо `build:`
- Образы из `ghcr.io/OWNER/systech-aidd-{bot,api,frontend,postgres}:latest`
- Сохранить все настройки environment, ports, networks из оригинального docker-compose.yml
- Все 4 сервиса используют образы из registry

### 4. Обновление Makefile

**Файл:** `Makefile`

Добавить команды для работы с prod-образами:

```makefile
docker-pull:        # Pull образов из registry
docker-up-prod:     # Запуск с prod образами (docker-compose -f docker-compose.prod.yml up -d)
docker-build-prod:  # Pull + up в одной команде
```

### 5. Документация GHCR Setup

**Файл:** `devops/doc/guides/ghcr-setup.md`

Пошаговая инструкция:

- Автоматическая авторизация через GITHUB_TOKEN
- Как сделать образы публичными (через GitHub Package Settings)
- Как локально авторизоваться для pull образов (опционально для public)
- Команды для работы с образами
- Troubleshooting

### 6. Обновление README

**Файл:** `README.md`

Добавить в начало:

- **Badge:** Build status из GitHub Actions
- **Секция:** "Docker Images" с ссылками на ghcr.io
- **Инструкция:** как использовать готовые образы из registry

Добавить секцию использования prod-образов:

```bash
# Использование готовых образов из GitHub Container Registry
docker-compose -f docker-compose.prod.yml up -d
# или
make docker-up-prod
```

### 7. Документация по работе с образами

**Файл:** `devops/doc/guides/using-registry-images.md`

Создать руководство:

- Локальная разработка: когда использовать local build vs registry images
- Команды для pull образов
- Как переключаться между режимами
- Планы на D2 (ручной deploy) и D3 (авто deploy)
- Примеры команд

### 8. Обновление DevOps Roadmap

**Файл:** `devops/doc/devops-roadmap.md`

Обновить статус спринта D1:

- Изменить статус с "📋 Planned" на "✅ Done"
- Добавить ссылки на созданные файлы

## Тестирование

1. **Локальная проверка workflow:**

   - Создать тестовую ветку
   - Сделать push
   - Проверить запуск workflow в GitHub Actions

2. **Проверка публикации:**

   - Убедиться что образы появились в ghcr.io
   - Проверить публичный доступ (без авторизации)

3. **Проверка pull и запуска:**

   - Локально выполнить `make docker-pull`
   - Запустить через `make docker-up-prod`
   - Проверить работу всех сервисов

## Требования MVP

- ✅ Простота настройки (минимум ручных действий)
- ✅ Автоматическая сборка на каждый push
- ✅ Публикация в ghcr.io
- ✅ Public доступ к образам
- ✅ Готовность к D2/D3 (использование образов на сервере)

## Не включаем (пока)

- ❌ Lint checks в CI
- ❌ Tests в CI
- ❌ Security scanning
- ❌ Multi-platform builds (arm64/amd64)
- ❌ Deployment stages (staging/production)

## Документы для создания

1. `.github/workflows/build.yml` - основной workflow
2. `docker-compose.prod.yml` - production compose
3. `devops/doc/github-actions-intro.md` - вводная документация
4. `devops/doc/guides/ghcr-setup.md` - настройка GHCR
5. `devops/doc/guides/using-registry-images.md` - работа с образами
6. `devops/SPRINT_D1_COMPLETE.md` - итоговый отчет о спринте

## Обновить существующие

1. `README.md` - badges, секция Docker Images
2. `Makefile` - команды для prod-образов
3. `devops/doc/devops-roadmap.md` - статус D1

### To-dos

- [ ] Создать devops/doc/github-actions-intro.md с документацией по GitHub Actions
- [ ] Создать .github/workflows/build.yml с matrix strategy для 4 образов (bot, api, frontend, postgres)
- [ ] Создать docker-compose.prod.yml для использования образов из ghcr.io
- [ ] Добавить команды в Makefile для работы с prod-образами
- [ ] Создать devops/doc/guides/ghcr-setup.md с инструкцией по GHCR
- [ ] Создать devops/doc/guides/using-registry-images.md с руководством по работе с образами
- [ ] Обновить README.md - добавить badges и секцию Docker Images
- [ ] Обновить devops/doc/devops-roadmap.md - статус D1 на Done
- [ ] Создать devops/SPRINT_D1_COMPLETE.md с отчетом о спринте

