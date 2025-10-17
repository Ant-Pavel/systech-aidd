# API Examples - Dashboard Statistics

Примеры запросов к API для получения статистики дашборда.

## Базовая информация

- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api`
- **Content-Type**: `application/json`

## Endpoints

### Health Check

Проверка состояния API сервера.

**Request:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "ok",
  "service": "dashboard-api",
  "version": "1.0.0"
}
```

---

### Get Dashboard Stats - 7 Days

Получение статистики за последние 7 дней (период по умолчанию).

**Request:**
```bash
curl -X GET "http://localhost:8000/api/stats?period=7d"
```

**Alternative (без параметра period):**
```bash
curl -X GET "http://localhost:8000/api/stats"
```

**Response:**
```json
{
  "metrics": {
    "total_messages": {
      "value": 3245,
      "change_percent": 12.5,
      "trend": "up",
      "description": "Trending up this month"
    },
    "active_conversations": {
      "value": 287,
      "change_percent": -3.2,
      "trend": "down",
      "description": "Down this period"
    },
    "avg_conversation_length": {
      "value": 11.3,
      "change_percent": 8.7,
      "trend": "up",
      "description": "Steady performance increase"
    }
  },
  "time_series": [
    {"date": "2025-10-11", "value": 445},
    {"date": "2025-10-12", "value": 478},
    {"date": "2025-10-13", "value": 412},
    {"date": "2025-10-14", "value": 523},
    {"date": "2025-10-15", "value": 491},
    {"date": "2025-10-16", "value": 456},
    {"date": "2025-10-17", "value": 440}
  ]
}
```

---

### Get Dashboard Stats - 30 Days

Получение статистики за последние 30 дней.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/stats?period=30d"
```

**Response:**
```json
{
  "metrics": {
    "total_messages": {
      "value": 13876,
      "change_percent": 15.3,
      "trend": "up",
      "description": "Trending up this month"
    },
    "active_conversations": {
      "value": 1145,
      "change_percent": 7.8,
      "trend": "up",
      "description": "Strong user retention"
    },
    "avg_conversation_length": {
      "value": 12.1,
      "change_percent": 4.5,
      "trend": "up",
      "description": "Steady performance increase"
    }
  },
  "time_series": [
    {"date": "2025-09-18", "value": 425},
    {"date": "2025-09-19", "value": 438},
    ...
    {"date": "2025-10-17", "value": 490}
  ]
}
```

---

### Get Dashboard Stats - 3 Months

Получение статистики за последние 3 месяца.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/stats?period=3m"
```

**Response:**
```json
{
  "metrics": {
    "total_messages": {
      "value": 42384,
      "change_percent": 18.9,
      "trend": "up",
      "description": "Trending up this month"
    },
    "active_conversations": {
      "value": 3542,
      "change_percent": 12.4,
      "trend": "up",
      "description": "Strong user retention"
    },
    "avg_conversation_length": {
      "value": 12.0,
      "change_percent": 5.8,
      "trend": "up",
      "description": "Meets growth projections"
    }
  },
  "time_series": [
    {"date": "2025-07-20", "value": 412},
    {"date": "2025-07-21", "value": 428},
    ...
    {"date": "2025-10-17", "value": 495}
  ]
}
```

---

## Error Responses

### Invalid Period

**Request:**
```bash
curl -X GET "http://localhost:8000/api/stats?period=invalid"
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["query", "period"],
      "msg": "Input should be '7d', '30d' or '3m'",
      "input": "invalid"
    }
  ]
}
```

---

## OpenAPI Documentation

### Swagger UI
Интерактивная документация с возможностью тестирования API:

```bash
# Открыть в браузере
http://localhost:8000/docs
```

### ReDoc
Альтернативная документация с удобным интерфейсом:

```bash
# Открыть в браузере
http://localhost:8000/redoc
```

### OpenAPI Schema (JSON)
Raw JSON схема OpenAPI:

```bash
curl -X GET "http://localhost:8000/openapi.json"
```

---

## Testing with Pretty Output

Использование `jq` для форматированного вывода:

```bash
# Установить jq (если не установлен)
# Ubuntu/Debian: sudo apt-get install jq
# macOS: brew install jq

# Запрос с форматированным выводом
curl -s "http://localhost:8000/api/stats?period=7d" | jq .

# Получить только метрики
curl -s "http://localhost:8000/api/stats?period=7d" | jq '.metrics'

# Получить только временной ряд
curl -s "http://localhost:8000/api/stats?period=7d" | jq '.time_series'
```

---

## Python Examples

### Using requests library

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Get stats for 7 days
response = requests.get("http://localhost:8000/api/stats?period=7d")
stats = response.json()
print(f"Total messages: {stats['metrics']['total_messages']['value']}")
```

### Using httpx (async)

```python
import httpx
import asyncio

async def get_stats():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/stats?period=30d")
        return response.json()

stats = asyncio.run(get_stats())
print(stats)
```

---

## JavaScript Examples

### Using fetch

```javascript
// Get stats
fetch('http://localhost:8000/api/stats?period=7d')
  .then(response => response.json())
  .then(data => {
    console.log('Total messages:', data.metrics.total_messages.value);
    console.log('Time series:', data.time_series);
  })
  .catch(error => console.error('Error:', error));
```

### Using axios

```javascript
import axios from 'axios';

// Get stats
const response = await axios.get('http://localhost:8000/api/stats', {
  params: { period: '7d' }
});

console.log(response.data);
```

---

## Running API Server

Для тестирования API сначала запустите сервер:

```bash
# Установить зависимости
make install

# Запустить API сервер
make api-run

# В другом терминале запустить тесты
make api-test
```

Сервер будет доступен по адресу: `http://localhost:8000`

