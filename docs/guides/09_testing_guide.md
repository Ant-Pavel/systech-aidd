# Testing Guide

Как писать и запускать тесты в проекте.

## Philosophy

**Принципы тестирования:**
- ✅ Покрытие минимум 70%
- ✅ Unit-тесты для всех публичных методов
- ✅ Моки для внешних зависимостей
- ✅ Тесты должны быть быстрыми и независимыми

## Test Structure

```
tests/
├── unit/                         # Unit-тесты
│   ├── test_config.py           # 12 тестов - Pydantic валидация
│   ├── test_conversation.py     # 12 тестов - история диалогов
│   ├── test_llm_client.py       # 10 тестов - LLM API с моками
│   ├── test_message_handler.py  # 7 тестов - обработка сообщений
│   └── test_command_handler.py  # 6 тестов - команды бота
└── conftest.py                   # Общие fixtures
```

## Running Tests

### All Tests

```bash
make test
```

Выполняет: `uv run pytest tests/ -v`

### Tests with Coverage

```bash
make test-cov
```

Создает HTML отчет: `htmlcov/index.html`

**Пример вывода:**
```
tests/unit/test_config.py::TestConfig::test_config_with_valid_data PASSED
...

Name                     Stmts   Miss  Cover
----------------------------------------------
src/config.py               12      0   100%
src/conversation.py         26      0   100%
src/llm_client.py           57      0   100%
----------------------------------------------
TOTAL                      190     35    82%
```

### Specific Test File

```bash
uv run pytest tests/unit/test_config.py -v
```

### Specific Test

```bash
uv run pytest tests/unit/test_config.py::TestConfig::test_config_with_valid_data -v
```

## Writing Tests

### Test Class Structure

```python
class TestClassName:
    """Тесты для класса ClassName."""

    def test_method_success(self) -> None:
        """Тест успешного выполнения метода."""
        # Arrange
        obj = ClassName()
        
        # Act
        result = obj.method()
        
        # Assert
        assert result == expected
```

**Требования:**
- ✅ Docstring на русском для каждого теста
- ✅ Type hints для всех параметров
- ✅ Arrange-Act-Assert структура

## Test Types

### 1. Configuration Tests (`test_config.py`)

**Что тестируем:**
- Валидация обязательных параметров
- Значения по умолчанию
- Приведение типов (str → int/float)
- Constraints (ge, le, min_length)

**Пример:**
```python
def test_config_missing_telegram_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Тест ошибки при отсутствии TELEGRAM_BOT_TOKEN."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    
    with pytest.raises(ValidationError):
        Config()
```

**Используем:**
- `monkeypatch` - для изменения environment variables

---

### 2. Conversation Tests (`test_conversation.py`)

**Что тестируем:**
- Добавление сообщений
- Получение истории
- Очистка истории
- Лимит сообщений (10 max)
- Изоляция между пользователями

**Пример:**
```python
def test_add_message_limit(self) -> None:
    """Тест ограничения количества сообщений."""
    conversation = Conversation(max_history_messages=3)
    
    for i in range(5):
        conversation.add_message(111, 222, "user", f"message {i}")
    
    history = conversation.get_history(111, 222)
    
    assert len(history) == 3  # Только последние 3
    assert history[0]["content"] == "message 2"
    assert history[2]["content"] == "message 4"
```

---

### 3. LLM Client Tests (`test_llm_client.py`)

**Что тестируем:**
- Успешные запросы к API
- Обработка ошибок (timeout, auth, rate limit)
- Загрузка системного промпта
- Добавление system message

**Используем:**
- `AsyncMock` - для async методов
- `patch` - для замены API клиента

**Пример:**
```python
async def test_get_response_success(self, llm_client: LLMClient) -> None:
    """Тест успешного запроса к LLM API."""
    messages = [{"role": "user", "content": "hello"}]
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hi there!"
    
    with patch.object(
        llm_client.client.chat.completions,
        "create",
        new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = mock_response
        
        response = await llm_client.get_response(messages)
        
        assert response == "Hi there!"
        mock_create.assert_called_once()
```

---

### 4. Message Handler Tests (`test_message_handler.py`)

**Что тестируем:**
- Полный flow обработки сообщения
- Взаимодействие с Conversation
- Взаимодействие с LLMClient
- Сохранение в историю

**Используем:**
- Protocol моки вместо реальных классов

**Пример:**
```python
async def test_handle_message(
    mock_llm: MagicMock,
    mock_conversation: MagicMock
) -> None:
    """Тест обработки сообщения."""
    handler = MessageHandler(
        llm_client=mock_llm,
        conversation=mock_conversation
    )
    
    mock_conversation.get_history.return_value = []
    mock_llm.get_response.return_value = "Response"
    
    result = await handler.handle_message(111, 222, "Hello")
    
    assert result == "Response"
    mock_conversation.add_message.assert_any_call(111, 222, "user", "Hello")
    mock_conversation.add_message.assert_any_call(111, 222, "assistant", "Response")
```

---

### 5. Command Handler Tests (`test_command_handler.py`)

**Что тестируем:**
- Команды /start, /help, /clear, /role
- Текст ответов
- Взаимодействие с Conversation

**Используем:**
- `AsyncMock` для aiogram Message
- Моки для проверки вызовов

**Пример:**
```python
async def test_start_command(self, command_handler: CommandHandler) -> None:
    """Тест команды /start."""
    message = AsyncMock(spec=Message)
    message.from_user.id = 12345
    
    await command_handler.start(message)
    
    message.answer.assert_called_once()
    args = message.answer.call_args[0]
    assert "нутрициолог" in args[0].lower()
```

## Fixtures

### Global Fixtures (`conftest.py`)

```python
@pytest.fixture
def sample_config_data() -> dict[str, str]:
    """Пример данных конфигурации для тестов."""
    return {
        "TELEGRAM_BOT_TOKEN": "test_token_123",
        "OPENROUTER_API_KEY": "test_key_123",
    }
```

### Local Fixtures (в test файле)

```python
@pytest.fixture
def llm_client() -> LLMClient:
    """Fixture для LLMClient без системного промпта."""
    return LLMClient(
        api_key="test_key",
        model="test_model",
        temperature=0.7,
        max_tokens=1000,
        timeout=30,
        system_prompt_path=None,
    )
```

## Mocking

### AsyncMock for Async Methods

```python
from unittest.mock import AsyncMock

mock_method = AsyncMock(return_value="result")
result = await mock_method()
```

### MagicMock for Sync Methods

```python
from unittest.mock import MagicMock

mock_obj = MagicMock()
mock_obj.method.return_value = "result"
result = mock_obj.method()
```

### Patch for External Dependencies

```python
from unittest.mock import patch

with patch('module.ClassName.method') as mock_method:
    mock_method.return_value = "result"
    # ... test code ...
```

### Protocol Mocks

```python
@pytest.fixture
def mock_conversation() -> MagicMock:
    """Mock для ConversationStorageProtocol."""
    mock = MagicMock(spec=ConversationStorageProtocol)
    mock.get_history.return_value = []
    mock.add_message.return_value = None
    mock.clear_history.return_value = None
    return mock
```

## Testing Async Code

### Pytest AsyncIO

Проект настроен на `asyncio_mode = "auto"` в `pyproject.toml`.

**Async test:**
```python
async def test_async_method(self) -> None:
    """Тест async метода."""
    result = await async_method()
    assert result == expected
```

**AsyncMock usage:**
```python
mock = AsyncMock(return_value="result")
result = await mock()
mock.assert_called_once()
```

## Test Coverage

### Current Coverage

**Target:** ≥ 70%

**Actual:** ~80%

### Coverage by Module

| Module | Coverage |
|--------|----------|
| config.py | 100% |
| conversation.py | 100% |
| llm_client.py | 100% |
| message_handler.py | 100% |
| command_handler.py | 100% |
| protocols.py | 100% |
| types.py | 100% |
| bot.py | 0% (точка входа) |

### View Coverage Report

```bash
make test-cov
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Common Patterns

### Testing Exceptions

```python
def test_error_handling(self) -> None:
    """Тест обработки ошибок."""
    with pytest.raises(ValidationError):
        Config()  # Missing required fields
```

### Testing Error Messages

```python
async def test_api_timeout(self) -> None:
    """Тест таймаута API."""
    with patch(...) as mock:
        mock.side_effect = APITimeoutError("Timeout")
        
        with pytest.raises(Exception) as exc_info:
            await llm_client.get_response(messages)
        
        assert "Timeout" in str(exc_info.value)
```

### Testing Calls

```python
def test_method_calls(self) -> None:
    """Тест вызовов методов."""
    mock = MagicMock()
    
    obj.method(mock)
    
    mock.some_method.assert_called_once()
    mock.some_method.assert_called_with("expected", "args")
    mock.some_method.assert_any_call("arg1")
```

### Testing Side Effects

```python
def test_side_effects(self) -> None:
    """Тест побочных эффектов."""
    mock = MagicMock()
    mock.side_effect = [1, 2, 3]
    
    assert mock() == 1
    assert mock() == 2
    assert mock() == 3
```

## Adding New Tests

### Step-by-Step

1. **Создать новый класс:**
   ```python
   class NewClass:
       def new_method(self) -> str:
           return "result"
   ```

2. **Создать test файл:**
   ```python
   # tests/unit/test_new_class.py
   
   class TestNewClass:
       """Тесты для NewClass."""
       
       def test_new_method(self) -> None:
           """Тест new_method."""
           obj = NewClass()
           result = obj.new_method()
           assert result == "result"
   ```

3. **Запустить тесты:**
   ```bash
   make test
   ```

4. **Проверить coverage:**
   ```bash
   make test-cov
   ```

## Best Practices

**✅ DO:**
- Писать тесты для всех публичных методов
- Использовать моки для внешних зависимостей
- Тестировать граничные случаи (edge cases)
- Тестировать ошибки (error handling)
- Использовать понятные имена тестов
- Добавлять docstring к каждому тесту

**❌ DON'T:**
- Тестировать приватные методы напрямую
- Делать тесты зависимыми друг от друга
- Использовать реальные API в тестах
- Игнорировать failing тесты
- Писать слишком сложные тесты

## Troubleshooting

### Тесты не запускаются

```bash
# Проверить установку pytest
uv run pytest --version

# Переустановить зависимости
make install
```

### Import errors в тестах

```bash
# Убедиться, что запускаете через uv
uv run pytest tests/

# Или через make
make test
```

### Async tests fail

```bash
# Проверить asyncio_mode в pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Next Steps

- 🔨 [Development Workflow](08_development_workflow.md) - workflow разработки
- ⚙️ [Configuration & Secrets](07_configuration_secrets.md) - тестирование конфигурации
- 🗺️ [Codebase Tour](04_codebase_tour.md) - где находятся тесты

