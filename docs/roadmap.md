# Roadmap проекта Systech AIDD Bot

> **Проект:** Специализированный ИИ-ассистент в виде Telegram-бота с ролевой специализацией  
> **Документация:** [Идея проекта](idea.md) | [Техническое видение](vision.md)

---

## Легенда статусов

| Статус | Иконка | Описание |
|--------|--------|----------|
| Planned | 📋 | Спринт запланирован, работа не начата |
| In Progress | 🚧 | Спринт в процессе выполнения |
| Completed | ✅ | Спринт завершен успешно |
| On Hold | ⏸️ | Спринт приостановлен |
| Cancelled | ❌ | Спринт отменен |

---

## Таблица спринтов

| Код | Название | Статус | Цель и описание | Состав работ | Тасклисты |
|-----|----------|--------|-----------------|--------------|-----------|
| **S0** | **MVP: Базовый бот-нутрициолог** | ✅ Completed | Создать рабочий MVP Telegram-бота с ролью нутрициолога, настроить инфраструктуру качества кода и тестирование | • Базовая инфраструктура бота<br>• LLM интеграция (Openrouter)<br>• История диалогов<br>• Команды управления<br>• Обработка ошибок<br>• Ролевая специализация<br>• Инструменты качества (ruff, mypy)<br>• Type safety + Protocols<br>• Pydantic Config + валидация<br>• Unit-тестирование (79% coverage) | [Основная разработка](tasklists/tasklist-S0.md)<br>[Технический долг](tasklists/tasklist-tech-debt-S0.md) |
| **S1** | **Персистентное хранение данных** | ✅ Completed | Реализовать сохранение истории диалогов в базе данных вместо текущего in-memory хранения. История диалогов должна сохраняться между перезапусками бота | • PostgreSQL + asyncpg + Alembic<br>• Docker Compose для БД<br>• Raw SQL запросы<br>• Soft delete стратегия<br>• Метаданные сообщений (created_at, message_length)<br>• Миграции БД<br>• Обновление документации | [План S1](.cursor/plans/s1-database-persistence-f5742ec9.plan.md)<br>[ADR 0001](adr/0001-postgresql-raw-sql-alembic.md) |

---

## Детали спринтов

### S0: MVP - Базовый бот-нутрициолог (✅ Completed)

**Период:** 2025-10-10 — 2025-10-11  
**Результат:** Полностью функциональный Telegram-бот с ролью нутрициолога, покрытие тестами 79%, все инструменты качества кода настроены

**Основные достижения:**
- ✅ Telegram-бот на aiogram 3.x с polling
- ✅ Интеграция с LLM через Openrouter (Claude Sonnet 3.5)
- ✅ Система управления историей диалогов (in-memory)
- ✅ Ролевая система через системные промпты
- ✅ Команды: `/start`, `/help`, `/clear`, `/new`, `/role`
- ✅ Инфраструктура качества: ruff, mypy (strict), pytest
- ✅ Type hints везде + Protocol абстракции (SOLID)
- ✅ Pydantic BaseSettings для конфигурации
- ✅ 47 unit-тестов, coverage 79.38%

**Технологический стек:**
- Python 3.11+, uv, aiogram, openai client
- Pydantic, pytest, ruff, mypy
- Make для автоматизации

**Ссылки на документацию:**
- [Основной тасклист](tasklists/tasklist-S0.md) - 6 итераций разработки функционала
- [Технический долг](tasklists/tasklist-tech-debt-S0.md) - 5 итераций улучшения качества кода

---

### S1: Персистентное хранение данных (✅ Completed)

**Период:** 2025-10-16  
**Результат:** Полностью функциональная система персистентного хранения истории диалогов в PostgreSQL с поддержкой soft delete и метаданных сообщений, покрытие тестами 78%

**Основные достижения:**
- ✅ PostgreSQL 16 через Docker Compose с health checks
- ✅ Система миграций на базе Alembic (async mode)
- ✅ Connection pool через asyncpg (5-10 соединений)
- ✅ Raw SQL запросы для полного контроля
- ✅ Таблица messages с индексами для оптимизации
- ✅ Soft delete стратегия (deleted_at timestamp)
- ✅ Метаданные сообщений: created_at, message_length
- ✅ DatabaseConversation реализует ConversationStorageProtocol
- ✅ Лимит истории (последние N сообщений)
- ✅ 9 новых unit-тестов для DatabaseConversation
- ✅ Coverage 78% (71 тест проходит)
- ✅ ADR 0001: PostgreSQL + Raw SQL + Alembic
- ✅ Обновлена документация (README, guides, vision)

**Технологический стек:**
- PostgreSQL 16 Alpine, Docker Compose
- asyncpg (асинхронный драйвер)
- Alembic (миграции), SQLAlchemy (только для Alembic)
- Raw SQL для прозрачности и производительности

**Ссылки на документацию:**
- [План S1](.cursor/plans/s1-database-persistence-f5742ec9.plan.md) - детальный план реализации
- [ADR 0001](adr/0001-postgresql-raw-sql-alembic.md) - архитектурное решение
- [Guide: Миграции БД](guides/10_database_migrations.md) - работа с Alembic
- [Guide: Быстрый старт](guides/01_getting_started.md) - обновлен для БД

---

