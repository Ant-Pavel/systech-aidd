# GitHub Actions: Введение

Краткое руководство по GitHub Actions для автоматизации сборки и публикации Docker образов.

## Что такое GitHub Actions?

**GitHub Actions** — это встроенная CI/CD платформа GitHub для автоматизации процессов разработки:
- Сборка и тестирование кода
- Публикация артефактов (Docker образы, пакеты)
- Развертывание на серверы
- Автоматизация любых задач по событиям в репозитории

### Основные концепции

**Workflow (Рабочий процесс)**
- YAML файл в `.github/workflows/`
- Описывает автоматизированный процесс
- Запускается по событиям (push, pull request, schedule, и т.д.)

**Job (Задание)**
- Набор шагов, выполняемых на одном runner
- Может выполняться параллельно с другими jobs
- По умолчанию jobs выполняются параллельно

**Step (Шаг)**
- Отдельная команда или action
- Выполняются последовательно внутри job

**Runner**
- Виртуальная машина, на которой выполняется workflow
- GitHub предоставляет бесплатные runners (Ubuntu, Windows, macOS)

## Triggers (Триггеры)

Workflow запускается по событиям в репозитории.

### Push - при каждом push в репозиторий

```yaml
on:
  push:
    branches:
      - main          # только main ветка
      - develop       # только develop ветка
      - '**'          # все ветки
```

### Pull Request - при создании/обновлении PR

```yaml
on:
  pull_request:
    branches:
      - main          # только PR в main
    types:
      - opened        # создание PR
      - synchronize   # новые коммиты в PR
      - reopened      # переоткрытие PR
```

### Workflow Dispatch - ручной запуск

```yaml
on:
  workflow_dispatch:  # кнопка "Run workflow" в GitHub UI
    inputs:           # можно добавить параметры
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
```

### Комбинированный trigger

```yaml
on:
  push:
    branches: ['main', 'develop']
  pull_request:
    branches: ['main']
  workflow_dispatch:
```

## Pull Request Workflow

### Типичный процесс работы с PR

1. **Разработчик создает ветку:**
   ```bash
   git checkout -b feature/new-feature
   git push origin feature/new-feature
   ```

2. **На push срабатывает CI:**
   - Проверяется код (lint, typecheck)
   - Запускаются тесты
   - Собираются артефакты (опционально)

3. **Создается Pull Request:**
   - Код проходит review
   - CI проверяет каждое обновление PR
   - Статус CI отображается в PR

4. **После approve и merge в main:**
   - Запускается основной workflow
   - Публикуются артефакты (Docker образы, пакеты)
   - Опционально: автоматический deploy

### Защита веток

В настройках репозитория можно требовать:
- Успешное прохождение CI перед merge
- Минимум N approvals
- Актуальность ветки с main

## Matrix Strategy

**Matrix strategy** позволяет запускать один job с разными параметрами параллельно.

### Пример: сборка нескольких Docker образов

```yaml
jobs:
  build:
    strategy:
      matrix:
        service: [bot, api, frontend, postgres]
    steps:
      - name: Build ${{ matrix.service }}
        run: |
          docker build -f devops/Dockerfile.${{ matrix.service }} \
            -t myapp-${{ matrix.service }}:latest .
```

**Результат:** 4 параллельных job, каждый собирает свой образ.

### Matrix с несколькими параметрами

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    python: ['3.10', '3.11', '3.12']
```

**Результат:** 6 jobs (3 версии Python × 2 ОС)

### Отказоустойчивость

```yaml
strategy:
  fail-fast: false  # продолжить даже если один job упал
  matrix:
    service: [bot, api, frontend]
```

## GitHub Container Registry (GHCR)

### Публикация образов в ghcr.io

GitHub предоставляет бесплатный Docker registry:
- **URL:** `ghcr.io`
- **Формат:** `ghcr.io/OWNER/IMAGE_NAME:TAG`
- **Доступ:** public или private

### Авторизация в workflow

```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**GITHUB_TOKEN** — автоматически доступен в каждом workflow, не требует настройки.

### Публикация образа

```yaml
- name: Build and push
  run: |
    docker build -t ghcr.io/${{ github.repository_owner }}/myapp:latest .
    docker push ghcr.io/${{ github.repository_owner }}/myapp:latest
```

### Public vs Private

**Private (по умолчанию):**
- Образ виден только вам и членам вашей организации
- Требует авторизации для pull

**Public:**
- Образ доступен всем без авторизации
- Настраивается в Package settings на GitHub

**Как сделать public:**
1. Перейти на страницу package: `https://github.com/OWNER/REPO/pkgs/container/IMAGE_NAME`
2. Package Settings → Change visibility → Public

## Secrets и Переменные

### GitHub Secrets

Безопасное хранение чувствительных данных (API ключи, пароли).

**Создание secret:**
- Settings → Secrets and variables → Actions → New repository secret

**Использование в workflow:**
```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
```

### Встроенные переменные

GitHub предоставляет множество переменных:

```yaml
${{ github.repository }}          # owner/repo
${{ github.repository_owner }}    # owner
${{ github.ref }}                 # refs/heads/main
${{ github.ref_name }}            # main
${{ github.sha }}                 # commit SHA (полный)
${{ github.run_number }}          # номер запуска workflow
${{ github.actor }}               # пользователь, запустивший workflow
```

## Кэширование

### Docker Layer Cache

Ускоряет сборку за счет переиспользования слоев:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ghcr.io/owner/image:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Результат:** последующие сборки могут быть в 5-10 раз быстрее.

### Cache Action

Кэширование зависимостей (npm, pip, etc.):

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

## Тегирование образов

### Стратегии тегирования

**latest + SHA:**
```yaml
tags: |
  ghcr.io/owner/image:latest
  ghcr.io/owner/image:sha-${{ github.sha }}
```

**latest + версия:**
```yaml
tags: |
  ghcr.io/owner/image:latest
  ghcr.io/owner/image:v1.2.3
```

**Условное тегирование:**
```yaml
- name: Tag as latest only on main
  if: github.ref == 'refs/heads/main'
  run: |
    docker tag myimage:build myimage:latest
    docker push myimage:latest
```

## Лучшие практики

### 1. Используйте конкретные версии actions
```yaml
# ✅ Хорошо
uses: actions/checkout@v4

# ❌ Плохо
uses: actions/checkout@main
```

### 2. Минимизируйте использование secrets
```yaml
# ✅ Используйте GITHUB_TOKEN где возможно
password: ${{ secrets.GITHUB_TOKEN }}

# ❌ Не создавайте лишние PAT токены
password: ${{ secrets.MY_CUSTOM_TOKEN }}
```

### 3. Оптимизируйте время выполнения
- Используйте matrix для параллелизма
- Включайте кэширование
- Минимизируйте checkout (sparse-checkout)

### 4. Обрабатывайте ошибки
```yaml
- name: Build
  run: make build
  continue-on-error: false  # остановить workflow при ошибке

- name: Notify on failure
  if: failure()
  run: echo "Build failed!"
```

### 5. Документируйте workflow
```yaml
name: Build and Publish Docker Images

on:
  push:  # Trigger on every push to build images

jobs:
  build:
    name: Build ${{ matrix.service }} image  # понятное имя job
```

## Пример полного workflow

```yaml
name: Build and Publish

on:
  push:
    branches: ['**']

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, api, frontend]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: devops/Dockerfile.${{ matrix.service }}
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/myapp-${{ matrix.service }}:latest
            ghcr.io/${{ github.repository_owner }}/myapp-${{ matrix.service }}:sha-${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Мониторинг и отладка

### Просмотр логов

Логи доступны в GitHub UI:
- Вкладка Actions → выбрать workflow → выбрать job → просмотр шагов

### Отладка workflow

```yaml
- name: Debug info
  run: |
    echo "Repository: ${{ github.repository }}"
    echo "Branch: ${{ github.ref_name }}"
    echo "SHA: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
```

### Re-run jobs

В UI можно перезапустить:
- Весь workflow
- Только упавшие jobs

## Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow syntax reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Actions Marketplace](https://github.com/marketplace?type=actions)

---

**Готово! 🚀 Теперь можно настроить автоматическую сборку образов!**

