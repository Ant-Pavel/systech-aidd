<!-- ecb8c27e-77a1-46e8-9ca2-9339334dbeb4 82ae836c-77a0-452b-915f-b891961eff6b -->
# Спринт 4: Реализация ИИ-чата

## Обзор

Реализовать веб-интерфейс чата на отдельной странице `/chat`, с сохранением истории в БД, заменить mock-статистику на реальные данные из БД и добавить потоковые ответы от LLM.

## Референсы

- **UI компоненты чата**: `frontend/doc/references/21st-ai-chat.md` - содержит полный код всех компонентов
- **Визуальный дизайн**: `frontend/doc/references/chat reference image.png` - референсное изображение
- **Техническое видение**: `frontend/doc/front-vision.md` - принципы разработки UI

## Ключевые технические решения

### Управление пользователями

- **Пользователи веб-чата**: Хранение в БД в таблице `messages`
- **Управление сессиями**: Session ID генерируется при первом визите, сохраняется в localStorage
- **Различение источников**: Добавить поле `source` в таблицу `messages` ('telegram' или 'web')
- **Web user_id**: Использовать отрицательные ID для веб-пользователей (начиная с -1)
- **Web chat_id**: Равен user_id (т.к. нет групповых чатов в веб)
- **Персистентность**: История сохраняется в БД и восстанавливается при повторном открытии

### Архитектура

- **Потоковая передача**: Server-Sent Events (SSE) для ответов LLM
- **Статистика**: Реальные запросы к БД (замена MockStatCollector)
- **Расположение чата**: Отдельная страница `/chat` с полноэкранным интерфейсом
- **Навигация**: Ссылка на чат с дашборда и обратно
- **Хранилище**: Переиспользовать `DatabaseConversation` для веб-чата
- **Database pool**: Использовать существующий `get_pool()` из `src/database.py`

## Реализация Backend

### 1. Миграция БД: добавление поля source

Создать Alembic миграцию для добавления поля в таблицу `messages`:

```sql
ALTER TABLE messages ADD COLUMN source VARCHAR(20) DEFAULT 'telegram';
CREATE INDEX idx_messages_source ON messages(source);
```

### 2. Обновление DatabaseConversation (`src/database_conversation.py`)

Добавить поддержку поля `source`:

- Обновить `add_message()`: добавить параметр `source: str = 'telegram'`
- `get_history()` и `clear_history()` работают без изменений
- Все существующие сообщения имеют source='telegram' по умолчанию

### 3. Обработчик веб-чата (`src/api/web_chat_handler.py`)

Создать обработчик для веб-чата с полной логикой обработки сообщений:

**Класс `WebChatHandler`**:

```python
class WebChatHandler:
    def __init__(
        self,
        database_conversation: DatabaseConversation,
        llm_client: LLMClientProtocol,
        max_history_messages: int
    ):
        self.db_conversation = database_conversation
        self.llm_client = llm_client
        self.session_to_user_id: dict[str, int] = {}
        self.next_user_id = -1  # Отрицательные ID для веб-пользователей
    
    def get_or_create_user_id(self, session_id: str) -> int:
        """Маппинг session_id → user_id"""
        if session_id not in self.session_to_user_id:
            self.session_to_user_id[session_id] = self.next_user_id
            self.next_user_id -= 1
        return self.session_to_user_id[session_id]
    
    async def handle_message_stream(
        self, session_id: str, message: str
    ) -> AsyncGenerator[str, None]:
        """
        Обработка сообщения со стримингом ответа.
        
        1. Получить user_id для session_id
        2. Сохранить сообщение пользователя в БД (source='web')
        3. Получить историю диалога
        4. Стримить ответ от LLM (yield chunks)
        5. После завершения стрима сохранить полный ответ в БД
        """
        user_id = self.get_or_create_user_id(session_id)
        chat_id = user_id  # Для веб chat_id = user_id
        
        # Сохранить сообщение пользователя
        await self.db_conversation.add_message(
            user_id, chat_id, "user", message, source="web"
        )
        
        # Получить историю
        history = await self.db_conversation.get_history(user_id, chat_id)
        
        # Добавить текущее сообщение
        messages = [*history, ChatMessage(role="user", content=message)]
        
        # Стримить ответ и накапливать
        full_response = ""
        async for chunk in self.llm_client.get_response_stream(messages):
            full_response += chunk
            yield chunk
        
        # Сохранить полный ответ
        await self.db_conversation.add_message(
            user_id, chat_id, "assistant", full_response, source="web"
        )
    
    async def get_history(self, session_id: str) -> list[ChatMessage]:
        """Получить историю для session_id"""
        user_id = self.get_or_create_user_id(session_id)
        chat_id = user_id
        return await self.db_conversation.get_history(user_id, chat_id)
```

**Ключевые моменты**:

- User message сохраняется **до** стриминга
- Assistant message сохраняется **после** стриминга (полный накопленный ответ)
- Маппинг session_id → user_id хранится в памяти

### 4. Роуты для чата (`src/api/routes.py`)

Добавить endpoints:

**POST `/api/chat/message`** - отправка сообщения (streaming):

```python
@router.post("/chat/message")
async def send_message(
    request: ChatRequest,
    web_chat_handler: WebChatHandler = Depends(get_web_chat_handler)
):
    async def event_generator():
        try:
            async for chunk in web_chat_handler.handle_message_stream(
                request.session_id, request.message
            ):
                # SSE формат
                yield f'data: {{"type":"token","content":"{chunk}"}}\n\n'
            
            yield f'data: {{"type":"done","content":""}}\n\n'
        except Exception as e:
            yield f'data: {{"type":"error","content":"{str(e)}"}}\n\n'
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**GET `/api/chat/history`** - получение истории:

```python
@router.get("/chat/history", response_model=list[ChatMessageResponse])
async def get_history(
    session_id: str,
    web_chat_handler: WebChatHandler = Depends(get_web_chat_handler)
):
    messages = await web_chat_handler.get_history(session_id)
    return [
        ChatMessageResponse(
            role=msg["role"],
            content=msg["content"],
            created_at=msg.get("created_at", "")
        )
        for msg in messages
    ]
```

Модели в `src/api/models.py`:

- `ChatRequest(session_id: str, message: str)`
- `ChatMessageResponse(role: str, content: str, created_at: str)`
- `StreamEvent(type: Literal["token", "done", "error"], content: str)`

### 5. Реальный сборщик статистики (`src/api/real_stat_collector.py`)

Реализовать статистику на основе БД:

- Класс `RealStatCollector`, реализующий `StatCollectorProtocol`
- Использует `get_pool()` из `src/database.py` для получения connection pool
- Методы: `get_dashboard_stats(period)` с SQL-агрегациями
- **Учет всех источников**: статистика включает сообщения из всех источников (Telegram и Web)
- Данные временных рядов через группировку по `created_at`

Необходимые SQL-запросы:

- Общее количество сообщений (WHERE deleted_at IS NULL AND created_at >= period_start)
- Активные диалоги (DISTINCT user_id, chat_id WHERE deleted_at IS NULL)
- Средняя длина диалога (AVG сообщений на диалог)
- Временной ряд (GROUP BY date WHERE deleted_at IS NULL)

### 6. Обновление API App (`src/api/app.py`)

- Импортировать `RealStatCollector` вместо `MockStatCollector`
- Создать глобальный экземпляр `WebChatHandler`
- Обновить `create_app()` для инициализации с LLMClient и DatabaseConversation
- Добавить dependency `get_web_chat_handler()`
```python
_web_chat_handler: WebChatHandler | None = None

def create_app(
    stat_collector: StatCollectorProtocol | None = None,
    llm_client: LLMClientProtocol | None = None,
    database_conversation: DatabaseConversation | None = None,
) -> FastAPI:
    global _stat_collector, _web_chat_handler
    
    _stat_collector = stat_collector or RealStatCollector()
    
    if llm_client and database_conversation:
        _web_chat_handler = WebChatHandler(
            database_conversation, llm_client, max_history_messages=20
        )
    
    # ... остальная инициализация

def get_web_chat_handler() -> WebChatHandler:
    if _web_chat_handler is None:
        raise RuntimeError("WebChatHandler not initialized")
    return _web_chat_handler
```


### 7. Поддержка потоковой передачи LLM (`src/llm_client.py`)

Добавить метод для стриминга:

```python
async def get_response_stream(
    self, messages: list[ChatMessage]
) -> AsyncGenerator[str, None]:
    """Стримить ответ от LLM по мере получения chunks"""
    try:
        # Добавить системный промпт
        final_messages = messages
        if self.system_prompt:
            system_message: ChatMessage = {
                "role": "system", "content": self.system_prompt
            }
            final_messages = [system_message, *messages]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=final_messages,  # type: ignore
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
            stream=True  # Включить стриминг
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    except Exception as e:
        logger.error(f"Error in LLM streaming: {e}", exc_info=True)
        raise
```

### 8. Обновление api_main.py

Обеспечить передачу зависимостей в `create_app()`:

- Использовать существующий `get_pool()` из `src/database.py`
- Создать экземпляры `LLMClient` и `DatabaseConversation`
- Передать их в `create_app()` вместе с `RealStatCollector`
```python
from src.database import get_pool, init_db_pool
from src.llm_client import LLMClient
from src.database_conversation import DatabaseConversation
from src.api.real_stat_collector import RealStatCollector

# При старте приложения
await init_db_pool(...)  # Уже есть в коде

llm_client = LLMClient(...)  # Создать из конфига
db_conversation = DatabaseConversation(max_history_messages=20)
stat_collector = RealStatCollector()

app = create_app(
    stat_collector=stat_collector,
    llm_client=llm_client,
    database_conversation=db_conversation
)
```


## Реализация Frontend

### 9. Установка зависимостей

```bash
cd frontend
pnpm add lucide-react @radix-ui/react-slot @radix-ui/react-avatar class-variance-authority
```

### 10. Создание UI-компонентов

**Референс**: `frontend/doc/references/21st-ai-chat.md` содержит полный код всех необходимых компонентов.

По структуре референса создать в `frontend/components/ui/`:

**`avatar.tsx`**: Radix UI аватар с fallback (из референса shadcn/avatar)

**`textarea.tsx`**: Базовое текстовое поле со стилизацией (из референса shadcn/textarea)

**`message-loading.tsx`**: Анимированные точки загрузки SVG (из референса jakobhoeg/message-loading)

**`chat-bubble.tsx`**: Пузырь сообщения с аватаром, варианты sent/received (из референса jakobhoeg/chat-bubble)

**`chat-input.tsx`**: Обертка textarea для ввода в чате (из референса jakobhoeg/chat-input)

**`chat-message-list.tsx`**: Прокручиваемый контейнер сообщений с авто-прокруткой (из референса chat-message-list.tsx)

Создать хук в `frontend/components/hooks/`:

**`use-auto-scroll.tsx`**: Логика авто-прокрутки для сообщений чата (из референса jakobhoeg/use-auto-scroll)

**Важно**: Компонент `button.tsx` уже существует в проекте, проверить совместимость с референсом.

### 11. Страница чата (`frontend/pages/chat.tsx`)

Создать новую страницу для чата:

**Структура**:

- Полноэкранный интерфейс чата (100vh)
- Header с заголовком "AI Assistant" и кнопкой возврата на дашборд
- ChatMessageList с историей сообщений (flex-1)
- ChatInput в footer (fixed внизу)

**State management**:

```typescript
const [messages, setMessages] = useState<ChatMessage[]>([])
const [isLoading, setIsLoading] = useState(false)
const [sessionId] = useState(() => getOrCreateSessionId())

// Загрузка истории при монтировании
useEffect(() => {
  loadHistory(sessionId)
}, [])
```

**Функция генерации session ID**:

```typescript
function getOrCreateSessionId(): string {
  let sessionId = localStorage.getItem('chat_session_id')
  if (!sessionId) {
    sessionId = crypto.randomUUID()
    localStorage.setItem('chat_session_id', sessionId)
  }
  return sessionId
}
```

**Layout**:

```typescript
<div className="flex flex-col h-screen bg-background">
  {/* Header */}
  <header className="border-b p-4">
    <div className="container mx-auto flex items-center justify-between">
      <h1>AI Assistant</h1>
      <Link href="/dashboard">Dashboard</Link>
    </div>
  </header>
  
  {/* Messages */}
  <main className="flex-1 overflow-hidden">
    <ChatMessageList>...</ChatMessageList>
  </main>
  
  {/* Input */}
  <footer className="border-t p-4">
    <form onSubmit={handleSubmit}>
      <ChatInput />
    </form>
  </footer>
</div>
```

### 12. Обновление дашборда (`frontend/pages/dashboard.tsx`)

Добавить ссылку на чат:

```typescript
import Link from "next/link"
import { MessageSquare } from "lucide-react"

// В header, рядом с ThemeToggle:
<Link href="/chat">
  <Button variant="outline" size="icon">
    <MessageSquare className="h-5 w-5" />
  </Button>
</Link>
```

### 13. API-клиент для чата (`frontend/lib/api.ts`)

Добавить функции:

**Получение истории**:

```typescript
export async function getChatHistory(sessionId: string): Promise<ChatMessage[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/chat/history?session_id=${sessionId}`
  )
  if (!response.ok) throw new Error('Failed to load chat history')
  return response.json()
}
```

**Отправка сообщения со стримингом**:

```typescript
export async function sendChatMessage(
  sessionId: string,
  message: string,
  onToken: (token: string) => void,
  onComplete: () => void,
  onError: (error: string) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message })
  })
  
  if (!response.ok) {
    onError('Failed to send message')
    return
  }
  
  // Parse SSE stream
  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  
  while (reader) {
    const { done, value } = await reader.read()
    if (done) break
    
    const text = decoder.decode(value)
    const lines = text.split('\n')
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6))
        if (data.type === 'token') onToken(data.content)
        else if (data.type === 'done') onComplete()
        else if (data.type === 'error') onError(data.content)
      }
    }
  }
}
```

### 14. Типы (`frontend/types/api.ts`)

Добавить типы для чата (единый формат с backend):

```typescript
export interface ChatMessage {
  role: "user" | "assistant"
  content: string
  created_at: string  // ISO format
}

export interface ChatRequest {
  session_id: string
  message: string
}

export interface StreamEvent {
  type: "token" | "done" | "error"
  content: string
}
```

## Тестирование

### Backend-тесты

- `tests/unit/test_web_chat_handler.py`: Маппинг session_id, стриминг, сохранение в БД
- `tests/unit/test_real_stat_collector.py`: Запросы к БД, фильтрация по source
- Обновить `tests/unit/test_api_routes.py`: Добавить тесты chat endpoints
- Обновить `tests/unit/test_database_conversation.py`: Тест нового поля source

### Frontend-тестирование

- Ручное тестирование: Взаимодействие с чатом, стриминг, восстановление истории
- Проверка совместимости с темной темой
- Тестирование адаптивности на мобильных устройствах
- Проверка сохранения session_id в localStorage
- Навигация между дашбордом и чатом

## Порядок реализации

**Backend и Frontend можно разрабатывать параллельно:**

**Backend (шаги 1-5)**:

1. **Миграция БД**: Добавить поле `source` в таблицу messages
2. **Backend-статистика**: RealStatCollector с учетом всех источников (Telegram и Web)
3. **Обновление DatabaseConversation**: Добавить параметр source
4. **Backend-обработчик чата**: WebChatHandler с полной логикой
5. **Инфраструктура стриминга**: Потоковый LLM, роуты чата с SSE

**Frontend (шаги 6-8)**:

6. **Frontend UI-компоненты**: Скопировать из `21st-ai-chat.md`, адаптировать
7. **Frontend-страница чата**: Полноэкранный интерфейс на `/chat`
8. **API-клиент**: Функции для истории и стриминга

**Интеграция (шаги 9-10)**:

9. **Интеграция**: Навигация между страницами, тестирование E2E
10. **Доработка**: Обработка ошибок, состояния загрузки, UX

## Файлы для создания

**Backend:**

- `alembic/versions/XXXX_add_source_field_to_messages.py` (миграция)
- `src/api/web_chat_handler.py`
- `src/api/real_stat_collector.py`
- `tests/unit/test_web_chat_handler.py`
- `tests/unit/test_real_stat_collector.py`

**Frontend:**

- `frontend/components/ui/avatar.tsx`
- `frontend/components/ui/textarea.tsx`
- `frontend/components/ui/message-loading.tsx`
- `frontend/components/ui/chat-bubble.tsx`
- `frontend/components/ui/chat-input.tsx`
- `frontend/components/ui/chat-message-list.tsx`
- `frontend/components/hooks/use-auto-scroll.tsx`
- `frontend/pages/chat.tsx` (новая страница)

## Файлы для изменения

**Backend:**

- `src/database_conversation.py`: Добавить параметр source
- `src/api/app.py`: Использовать RealStatCollector, добавить WebChatHandler
- `src/api/routes.py`: Добавить chat endpoints
- `src/api/models.py`: Добавить модели для чата
- `src/llm_client.py`: Добавить метод стриминга
- `api_main.py`: Обеспечить передачу зависимостей в create_app
- `tests/unit/test_database_conversation.py`: Тесты для source

**Frontend:**

- `frontend/pages/dashboard.tsx`: Добавить ссылку на чат
- `frontend/lib/api.ts`: Добавить функции API чата
- `frontend/types/api.ts`: Добавить типы для чата
- `frontend/package.json`: Добавить зависимости

## Критерии успеха

- ✅ Страница `/chat` доступна и открывается
- ✅ Полноэкранный интерфейс чата работает
- ✅ Навигация между дашбордом и чатом функционирует
- ✅ Сообщения отправляются и стримятся токен за токеном
- ✅ История чата сохраняется в БД
- ✅ История восстанавливается при повторном открытии
- ✅ Session ID сохраняется в localStorage
- ✅ Дашборд показывает реальную статистику из БД (все источники: Telegram и Web)
- ✅ Темная тема работает корректно на обеих страницах
- ✅ Адаптивный дизайн для мобильных устройств
- ✅ Обработка ошибок сети/LLM

### To-dos

- [x] Создать Alembic миграцию для добавления поля source в таблицу messages
- [x] Обновить DatabaseConversation: добавить параметр source в add_message()
- [x] Реализовать RealStatCollector с запросами к БД (учет всех источников: Telegram и Web)
- [x] Создать WebChatHandler с методами handle_message_stream() и get_history()
- [x] Добавить поддержку стриминга в LLMClient с async generator
- [x] Реализовать endpoints: POST /api/chat/message (SSE) и GET /api/chat/history
- [x] Обновить api/app.py: использовать RealStatCollector и WebChatHandler с зависимостями
- [x] Обновить api_main.py: создать и передать LLMClient, DatabaseConversation в create_app()
- [x] Установить необходимые npm-пакеты для UI-компонентов чата
- [x] Создать базовые UI-компоненты: avatar, textarea, message-loading
- [x] Создать чат-компоненты: chat-bubble, chat-input, chat-message-list, use-auto-scroll
- [x] Создать страницу /chat с полноэкранным интерфейсом и localStorage
- [x] Реализовать API-клиент: getChatHistory() и sendChatMessage() со стримингом SSE
- [x] Добавить навигацию: ссылка на чат с дашборда и кнопка возврата
- [ ] Написать unit-тесты для WebChatHandler, RealStatCollector и обновить тесты DatabaseConversation
- [ ] Доработать UX: обработка ошибок, состояния загрузки, адаптивность, темная тема