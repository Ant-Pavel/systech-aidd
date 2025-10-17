<!-- ac2d0bc9-1fa0-4818-abfd-0992a59d29a9 d71f2d9b-0243-41fc-94ba-64f92bb6b3a4 -->
# Sprint 1: Mock API для дашборда статистики

## Цель

Создать Mock API для frontend дашборда, который предоставляет статистику по диалогам на основе тестовых данных. Спроектировать контракт API и интерфейс сборщика статистики для последующей реализации Real версии.

## Архитектура

```
FastAPI App
    ↓
StatCollectorProtocol (interface)
    ↓
MockStatCollector (реализация с фейковыми данными)
```

## Функциональные требования к дашборду

На основе референса (`frontend/reference/referenceImg.jpg`) дашборд должен содержать:

**3 метрики (карточки):**

1. Общее кол-во сообщений (Total Messages) - с процентным изменением
2. Активные диалоги (Active Conversations) - с процентным изменением  
3. Средняя длина диалога (Avg Conversation Length) - с процентным изменением

**График:**

- Временной ряд сообщений с фильтрацией по периодам (Last 7 days, Last 30 days, Last 3 months)

## Реализация

### 1. Создать документ с требованиями

Файл: `frontend/doc/dashboard-requirements.md`

- Функциональные требования к дашборду
- Описание метрик и их расчета
- Требования к API контракту

### 2. Спроектировать data models

Файл: `src/api/models.py`

Создать Pydantic модели для API response:

- `MetricCard` - данные для одной карточки метрики (значение, процент изменения, тренд, описание)
- `TimeSeriesPoint` - точка на графике (дата, значение)
- `DashboardStats` - полная статистика (метрики + временной ряд)

### 3. Создать Protocol для StatCollector

Файл: `src/api/protocols.py`

```python
class StatCollectorProtocol(Protocol):
    async def get_dashboard_stats(self, period: str) -> DashboardStats:
        """Получить статистику для дашборда за указанный период."""
        ...
```

### 4. Реализовать MockStatCollector

Файл: `src/api/mock_stat_collector.py`

- Генерация реалистичных метрик с изменениями
- Генерация временных рядов для графика (разные периоды)
- Использование `random` для вариативности данных
- Логика расчета процентных изменений

### 5. Создать FastAPI приложение

Файл: `src/api/app.py`

- Инициализация FastAPI с метаданными (title, version, description)
- Настройка CORS для frontend
- Dependency injection для StatCollector
- Health check endpoint (`/health`)

### 6. Создать API endpoint

Файл: `src/api/routes.py`

- `GET /api/stats?period={period}` - получение статистики
- Query parameter: `period` (7d, 30d, 3m) с валидацией
- Response: `DashboardStats` model
- Автоматическая генерация OpenAPI документации

### 7. Создать entrypoint

Файл: `api_main.py` (в корне проекта)

- Запуск FastAPI через uvicorn
- Настройка логирования
- Использование MockStatCollector по умолчанию

### 8. Добавить зависимости

Обновить `pyproject.toml`:

- `fastapi>=0.100.0`
- `uvicorn[standard]>=0.23.0`

### 9. Добавить команды в Makefile

```makefile
api-run:      # Запуск API сервера (dev mode)
api-test:     # Тестирование API endpoint (curl)
```

### 10. Создать тесты

Файл: `tests/unit/test_mock_stat_collector.py`

- Тесты генерации метрик
- Тесты расчета процентных изменений
- Тесты генерации временных рядов для разных периодов

Файл: `tests/unit/test_api_routes.py`

- Тесты API endpoint (FastAPI TestClient)
- Тесты валидации параметров
- Тесты health check

### 11. Создать примеры запросов для тестирования

Файл: `frontend/doc/api-examples.md`

- Примеры curl запросов к API
- Примеры с разными периодами (7d, 30d, 3m)
- Примеры ответов API
- Health check запрос

### 12. Сохранить копию плана

Файл: `frontend/doc/plans/f1-mock-api-plan.md`

- Копия текущего плана для истории
- Будет использоваться как ссылка в roadmap

### 13. Актуализировать roadmap

Обновить `docs/frontend-roadmap.md`:

- Изменить статус F-S1 на "✅ Completed"
- Добавить ссылку на план реализации (frontend/doc/plans/f1-mock-api-plan.md)

## Структура файлов

```
src/api/
  ├── __init__.py
  ├── app.py                    # FastAPI приложение
  ├── routes.py                 # API endpoints
  ├── models.py                 # Pydantic models
  ├── protocols.py              # StatCollectorProtocol
  └── mock_stat_collector.py    # Mock реализация

api_main.py                     # Entrypoint для API
frontend/doc/
  └── dashboard-requirements.md # Требования к дашборду
```

## Автоматическая документация API

FastAPI автоматически генерирует:

- OpenAPI (Swagger UI): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON schema: `http://localhost:8000/openapi.json`

## Пример API Response

```json
{
  "metrics": {
    "total_messages": {
      "value": 12543,
      "change_percent": 12.5,
      "trend": "up",
      "description": "Total messages this period"
    },
    "active_conversations": {
      "value": 1234,
      "change_percent": -5.2,
      "trend": "down",
      "description": "Currently active conversations"
    },
    "avg_conversation_length": {
      "value": 8.7,
      "change_percent": 3.1,
      "trend": "up",
      "description": "Average messages per conversation"
    }
  },
  "time_series": [
    {"date": "2025-06-01", "value": 450},
    {"date": "2025-06-02", "value": 520},
    ...
  ]
}
```

### To-dos

- [ ] Создать документ с функциональными требованиями к дашборду (frontend/doc/dashboard-requirements.md)
- [ ] Спроектировать Pydantic models для API response (src/api/models.py)
- [ ] Создать StatCollectorProtocol интерфейс (src/api/protocols.py)
- [ ] Реализовать MockStatCollector с генерацией тестовых данных (src/api/mock_stat_collector.py)
- [ ] Создать FastAPI приложение с CORS и dependency injection (src/api/app.py)
- [ ] Реализовать API endpoint GET /api/stats с валидацией (src/api/routes.py)
- [ ] Создать entrypoint для запуска API сервера (api_main.py)
- [ ] Добавить FastAPI и uvicorn в pyproject.toml
- [ ] Добавить команды api-run и api-test в Makefile
- [ ] Написать unit тесты для MockStatCollector (tests/unit/test_mock_stat_collector.py)
- [ ] Написать unit тесты для API routes (tests/unit/test_api_routes.py)
- [ ] Обновить docs/frontend-roadmap.md со ссылкой на план