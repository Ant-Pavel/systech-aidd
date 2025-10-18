# DevOps Roadmap

## Общая концепция

MVP DevOps roadmap для быстрого прохождения пути от локального запуска до автоматического развертывания на удаленный сервер. Фокус на простоте, скорости и практической ценности.

## Принципы

- **MVP подход**: минимум функциональности для достижения цели
- **Быстрая доставка**: от локальной разработки до продакшена за 4 спринта
- **Простота**: без преждевременной оптимизации и избыточной инфраструктуры
- **Итеративность**: небольшие шаги с проверкой результата

## Спринты

| Спринт | Описание | Статус | План |
|--------|----------|--------|------|
| **D0** | Basic Docker Setup | ✅ Done | [plan](plans/sprint-D0-plan.md) |
| **D1** | Build & Publish | ✅ Done | [summary](../SPRINT_D1_COMPLETE.md) |
| **D2** | Развертывание на сервер | 📋 Planned | [plan](plans/sprint-D2-plan.md) |
| **D3** | Auto Deploy | 📋 Planned | [plan](plans/sprint-D3-plan.md) |

**Статусы:**
- 📋 Planned - запланировано
- 🚧 In Progress - в работе
- ✅ Done - выполнено
- ⏸️ On Hold - приостановлено

---

## Спринт D0: Basic Docker Setup

**Цель:** Запустить все сервисы локально через `docker-compose` одной командой.

**Состав работ:**
- Все Dockerfiles должны быть в devops/Dockerfile.*
- Создать `Dockerfile` для каждого сервиса (bot, api, frontend)
- Обновить `docker-compose.yml` для управления всеми 4 сервисами
- Создать `.dockerignore` файлы для оптимизации сборки
- Настроить сетевое взаимодействие между сервисами
- Обеспечить правильную инициализацию PostgreSQL и миграций
- Проверить работоспособность: `docker-compose up` запускает весь стек локально
- Протестировать работу бота и фронта
- Обновить документацию с инструкциями по запуску

**Сервисы:**
1. **Bot** - Telegram бот (Python + UV)
2. **API** - FastAPI сервис статистики (Python + UV)
3. **Frontend** - веб-интерфейс (Next.js + pnpm)
4. **PostgreSQL** - база данных (уже есть в docker-compose.yml)

**Ожидаемые файлы:**
- `Dockerfile.bot`
- `Dockerfile.api`
- `Dockerfile.frontend`
- `docker-compose.yml` (обновленный)
- `.dockerignore` (корневой + специфичные для сервисов)
- `README.md` (обновленная секция запуска)

---

## Спринт D1: Build & Publish ✅

**Цель:** Автоматическая сборка и публикация Docker образов в GitHub Container Registry при push в любую ветку.

**Статус:** ✅ Выполнено

**Состав работ:**
- ✅ Создать GitHub Actions workflow для сборки образов
- ✅ Настроить аутентификацию в GitHub Container Registry (ghcr.io)
- ✅ Собирать 4 образа (bot, api, frontend, postgres) параллельно с matrix strategy
- ✅ Тегировать образы (`latest`, `sha-<commit>`, `branch-<name>`)
- ✅ Публиковать образы в ghcr.io с public доступом
- ✅ Добавить badges статуса сборки в README
- ✅ Создать инструкции по работе с GHCR и образами
- ✅ Создать docker-compose.prod.yml для использования образов из registry
- ✅ Добавить команды в Makefile для работы с prod-образами

**Созданные файлы:**
- `.github/workflows/build.yml` - GitHub Actions workflow
- `docker-compose.prod.yml` - для использования образов из registry
- `devops/doc/github-actions-intro.md` - введение в GitHub Actions
- `devops/doc/guides/ghcr-setup.md` - настройка GHCR
- `devops/doc/guides/using-registry-images.md` - работа с образами
- `README.md` (обновлен с badges и секцией Docker Images)
- `Makefile` (добавлены команды для prod-образов)
- `devops/SPRINT_D1_COMPLETE.md` - отчет о спринте

**Подробности:** См. [devops/SPRINT_D1_COMPLETE.md](../SPRINT_D1_COMPLETE.md)

---

## Спринт D2: Развертывание на сервер

**Цель:** Развернуть приложение на удаленном сервере вручную по детальной инструкции.

**Контекст:** Предоставлен готовый сервер (IP адрес, SSH ключ, Docker установлен).

**Состав работ:**
- Создать пошаговую инструкцию ручного деплоя
- Описать процесс SSH подключения с использованием ключа
- Подготовить шаблон production конфигурации (`.env.production`)
- Описать процесс копирования конфигурации на сервер
- Настроить `docker login` к ghcr.io на сервере
- Описать процесс загрузки образов (`docker-compose pull`)
- Описать запуск сервисов (`docker-compose up -d`)
- Создать скрипт проверки работоспособности
- Описать процесс запуска миграций БД

**Ожидаемые файлы:**
- `devops/doc/guides/manual-deploy.md`
- `.env.production` (шаблон)
- `scripts/deploy-check.sh`

---

## Спринт D3: Auto Deploy

**Цель:** Автоматическое развертывание на сервер через GitHub Actions по кнопке (workflow_dispatch).

**Состав работ:**
- Создать GitHub Actions workflow для деплоя
- Настроить ручной trigger (workflow_dispatch) для контролируемых релизов
- Реализовать SSH подключение к серверу из GitHub Actions
- Автоматизировать pull новых образов на сервере
- Автоматизировать перезапуск сервисов через `docker-compose`
- Добавить проверку работоспособности после деплоя
- Настроить уведомления о статусе деплоя
- Создать инструкцию по настройке GitHub secrets (SSH_KEY, HOST, USER)
- Добавить кнопку "Deploy" в README

**Ожидаемые файлы:**
- `.github/workflows/deploy.yml`
- `devops/doc/guides/auto-deploy-setup.md`
- `README.md` (обновленный с кнопкой Deploy)

---

## Процесс работы

1. **Plan Mode**: перед каждым спринтом создается детальный план в `devops/doc/plans/`
2. **Implementation**: выполнение задач из плана
3. **Testing**: проверка работоспособности
4. **Documentation**: обновление ссылок в роадмапе и статуса спринта

## Архитектура развертывания

```
┌─────────────────────────────────────────────────┐
│  Developer Machine                              │
│  ┌──────────────────────────────────────────┐  │
│  │  docker-compose up                       │  │
│  │  ├─ PostgreSQL                           │  │
│  │  ├─ Bot                                   │  │
│  │  ├─ API                                   │  │
│  │  └─ Frontend                              │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                    │
                    │ git push
                    ▼
┌─────────────────────────────────────────────────┐
│  GitHub                                         │
│  ┌──────────────────────────────────────────┐  │
│  │  GitHub Actions                          │  │
│  │  ├─ Build Images → ghcr.io              │  │
│  │  └─ Deploy (manual trigger)              │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                    │
                    │ SSH + docker-compose
                    ▼
┌─────────────────────────────────────────────────┐
│  Production Server                              │
│  ┌──────────────────────────────────────────┐  │
│  │  docker-compose (production)             │  │
│  │  ├─ PostgreSQL                           │  │
│  │  ├─ Bot                                   │  │
│  │  ├─ API                                   │  │
│  │  └─ Frontend                              │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Технологический стек

- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Registry**: GitHub Container Registry (ghcr.io)
- **Deployment**: SSH + docker-compose
- **Monitoring**: docker-compose logs (MVP)

## Следующие шаги после MVP

После завершения базового роадмапа (D0-D3) можно рассмотреть:

- Мониторинг и логирование (Prometheus, Grafana, Loki)
- Автоматическое тестирование в CI/CD
- Blue-green deployment
- Резервное копирование БД
- HTTPS и reverse proxy (nginx/traefik)
- Secrets management (Vault)
- Kubernetes (если потребуется масштабирование)

Но это **НЕ MVP** - фокус на D0-D3!

