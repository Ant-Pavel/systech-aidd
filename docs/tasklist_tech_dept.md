# План устранения технического долга Systech AIDD Bot

## 📊 Отчет по прогрессу

| Итерация | Описание                        | Статус       | Дата завершения |
|----------|---------------------------------|--------------|-----------------|
| 1️⃣       | Инструменты качества кода       | ✅ Завершено | 2025-10-11      |
| 2️⃣       | Type safety (type hints)        | ✅ Завершено | 2025-10-11      |
| 3️⃣       | SOLID: Protocols и абстракции   | ⏳ Не начато | -               |
| 4️⃣       | Pydantic Config + валидация     | ⏳ Не начато | -               |
| 5️⃣       | Unit-тестирование               | ⏳ Не начато | -               |

**Легенда статусов:**
- ⏳ Не начато
- 🚧 В работе
- ✅ Завершено
- ⚠️ Заблокировано

---

## 🎯 Итерация 1: Инструменты качества кода

**Цель:** Настроить ruff (форматтер + линтер), mypy (type checker), pytest

**Тестирование:** Запустить `make lint`, `make format`, `make typecheck`, `make test`

### Задачи:
- [x] Обновить `pyproject.toml` с dev-зависимостями (ruff, mypy, pytest, pytest-asyncio, pytest-cov)
- [x] Настроить ruff в `[tool.ruff]` (line-length=100, select правила)
- [x] Настроить mypy в `[tool.mypy]` (strict=true, python_version="3.11")
- [x] Настроить pytest в `[tool.pytest.ini_options]` (testpaths, markers)
- [x] Обновить `Makefile` с командами: lint, format, typecheck, test, test-cov, quality (все вместе)
- [x] Запустить `make format` на всей кодовой базе
- [x] Запустить `make lint` и убедиться в отсутствии критичных ошибок
- [x] Создать структуру директорий `tests/unit/` и `tests/integration/`
- [x] Создать `tests/conftest.py` для fixtures
- [x] Обновить файлы правил `*.mdc` и `vision.md` на соответствие сделанным изменениям

**Проверка качества:** `make quality` проходит без ошибок (кроме mypy - ждем итерацию 2)

---

## 🎯 Итерация 2: Type Safety (type hints)

**Цель:** Добавить type hints во все модули, пройти mypy strict mode

**Тестирование:** `make typecheck` проходит без ошибок

### Задачи:
- [x] Добавить type hints в `src/config.py` (все методы и атрибуты)
- [x] Добавить type hints в `src/conversation.py` (включая return types)
- [x] Добавить type hints в `src/llm_client.py` (async методы)
- [x] Добавить type hints в `src/message_handler.py`
- [x] Добавить type hints в `src/bot.py` (включая aiogram типы)
- [x] Добавить type hints в `main.py`
- [x] Импортировать типы из `typing` (Optional, Protocol, Any если нужно)
- [x] Запустить `make typecheck` и устранить все ошибки
- [x] Проверить работоспособность бота: `make run`
- [x] Обновить файлы правил `*.mdc` и `vision.md` на соответствие сделанным изменениям

**Проверка качества:** `mypy src/ --strict` проходит без ошибок

---

## 🎯 Итерация 3: SOLID - Protocols и абстракции

**Цель:** Улучшить DIP (Dependency Inversion Principle) через Protocol

**Тестирование:** `make typecheck` проходит без ошибок, бот работает корректно

### Задачи:
- [ ] Создать `src/protocols.py` с Protocol интерфейсами
- [ ] Определить `ConversationStorageProtocol` (add_message, get_history, clear_history)
- [ ] Определить `LLMClientProtocol` (get_response)
- [ ] Обновить type hints в `MessageHandler` для использования Protocol
- [ ] Обновить type hints в `TelegramBot` для использования Protocol
- [ ] Убедиться, что конкретные классы соответствуют Protocol (mypy проверит)
- [ ] Запустить `make typecheck` - должно пройти без ошибок
- [ ] Проверить работоспособность бота: `make run`
- [ ] Обновить файлы правил `*.mdc` и `vision.md` на соответствие сделанным изменениям

**Проверка качества:** Код использует абстракции, легко заменить реализацию

---

## 🎯 Итерация 4: Pydantic Config + валидация

**Цель:** Заменить Config на Pydantic BaseSettings, улучшить валидацию

**Тестирование:** Бот запускается, невалидная конфигурация выбрасывает понятные ошибки

### Задачи:
- [ ] Добавить `pydantic>=2.0.0` и `pydantic-settings>=2.0.0` в зависимости
- [ ] Переписать `src/config.py` на `pydantic_settings.BaseSettings`
- [ ] Добавить валидаторы для параметров (Field с constraints)
- [ ] Добавить `model_config` с `env_file = ".env"`
- [ ] Использовать Pydantic типы (PositiveInt, PositiveFloat, HttpUrl если нужно)
- [ ] Проверить автоматическое приведение типов (str -> int, str -> float)
- [ ] Проверить понятные ошибки валидации (ValidationError)
- [ ] Запустить `make typecheck` - должно пройти без ошибок
- [ ] Запустить `make quality` (без test) - проверка форматирования, линтинга, типов
- [ ] Проверить работоспособность бота: `make run`
- [ ] Обновить файлы правил `*.mdc` и `vision.md` на соответствие сделанным изменениям

**Проверка качества:** Config имеет строгую валидацию, понятные сообщения об ошибках

---

## 🎯 Итерация 5: Unit-тестирование

**Цель:** Написать unit-тесты для всех модулей, достичь минимум 70% покрытия

**Тестирование:** `make test-cov` показывает coverage ≥ 70%

### Задачи:
- [ ] Написать `tests/unit/test_config.py` (валидация Pydantic, defaults, missing keys)
- [ ] Написать `tests/unit/test_conversation.py` (add, get, clear, limit)
- [ ] Написать `tests/unit/test_llm_client.py` (моки для API, обработка ошибок)
- [ ] Написать `tests/unit/test_message_handler.py` (моки для Protocol зависимостей)
- [ ] Написать `tests/unit/test_bot.py` (команды /start, /help, /clear)
- [ ] Добавить fixtures в `tests/conftest.py` (config, conversation, мок-объекты)
- [ ] Использовать `pytest-asyncio` для async тестов
- [ ] Использовать `unittest.mock` для моков внешних зависимостей
- [ ] Запустить `make test-cov` и убедиться в покрытии ≥ 70%
- [ ] Запустить `make quality` - полная проверка всего pipeline
- [ ] Обновить файлы правил `*.mdc` и `vision.md` на соответствие сделанным изменениям

**Проверка качества:** `pytest --cov=src --cov-report=term-missing` показывает ≥ 70%

---

## 📝 Примечания

### Команды Make (после итерации 1):
```bash
make install         # Установка зависимостей (включая dev)
make run             # Запуск бота
make format          # Форматирование кода (ruff format)
make lint            # Линтинг (ruff check)
make typecheck       # Type checking (mypy)
make test            # Запуск тестов (pytest)
make test-cov        # Тесты с покрытием (pytest --cov)
make quality         # Полная проверка (format + lint + typecheck + test)
make quality-no-test # Проверка без тестов (format + lint + typecheck) - для итераций 3-4
make clean           # Очистка временных файлов
```

### Принципы работы:
- Следуй @conventions.md при разработке
- Все детали архитектуры в @vision.md
- Запускай `make quality` перед коммитом
- Тестируй после каждой итерации
- Коммиты на русском, атомарные изменения
- Покрытие тестами должно быть ≥ 70%
- Все проверки должны проходить через Make (не используем pre-commit хуки)

### Порядок выполнения:
1. Итерация выполняется полностью
2. Перед переходом к следующей итерации - полная проверка `make quality`
3. Обязательно обновляем документацию (правила и vision) в конце каждой итерации
4. Коммит после завершения итерации

---

## 🎓 Обучающие материалы

### Type Hints & Protocols
- PEP 484 (Type Hints)
- PEP 544 (Protocols)
- typing module documentation

### Testing
- pytest documentation
- pytest-asyncio для async тестов
- unittest.mock для моков

### Code Quality Tools
- ruff: современный линтер + форматтер (замена black + flake8 + isort)
- mypy: статический type checker
- pytest + coverage: тестирование и покрытие

### Pydantic
- pydantic v2 documentation
- pydantic-settings для конфигурации
- Field validators и constraints

