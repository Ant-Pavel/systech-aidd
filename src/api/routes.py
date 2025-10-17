"""API endpoints для дашборда и веб-чата."""

import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.api.app import get_stat_collector, get_web_chat_handler
from src.api.models import ChatMessageResponse, ChatRequest, DashboardStats
from src.api.protocols import StatCollectorProtocol
from src.api.web_chat_handler import WebChatHandler

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    period: Annotated[
        Literal["7d", "30d", "3m"],
        Query(description="Период для статистики: 7d, 30d, 3m"),
    ] = "7d",
    stat_collector: StatCollectorProtocol = Depends(get_stat_collector),  # noqa: B008
) -> DashboardStats:
    """Получить статистику для дашборда за указанный период.

    Args:
        period: Период для статистики (по умолчанию '7d')
        stat_collector: Инжектируемый сборщик статистики

    Returns:
        DashboardStats: Полная статистика включая метрики и временной ряд

    Raises:
        HTTPException: При ошибке получения статистики
    """
    try:
        stats = await stat_collector.get_dashboard_stats(period)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard stats: {e!s}",
        ) from e


# ===== Endpoints для веб-чата =====


@router.post("/chat/message")
async def send_message(
    request: ChatRequest,
    web_chat_handler: WebChatHandler = Depends(get_web_chat_handler),  # noqa: B008
) -> StreamingResponse:
    """Отправить сообщение в чат и получить streaming ответ.

    Args:
        request: Запрос с session_id и сообщением пользователя
        web_chat_handler: Инжектируемый обработчик веб-чата

    Returns:
        StreamingResponse: SSE stream с токенами ответа

    Raises:
        HTTPException: При ошибке обработки сообщения
    """

    async def event_generator():
        """Генератор SSE events для стриминга ответа."""
        try:
            async for chunk in web_chat_handler.handle_message_stream(
                request.session_id, request.message
            ):
                # Экранируем специальные символы для JSON
                escaped_chunk = chunk.replace('"', '\\"').replace("\n", "\\n")
                # SSE формат: data: {JSON}\n\n
                yield f'data: {{"type":"token","content":"{escaped_chunk}"}}\n\n'

            # Сигнал завершения
            yield f'data: {{"type":"done","content":""}}\n\n'

        except Exception as e:
            # Отправляем ошибку как SSE event
            error_msg = str(e).replace('"', '\\"')
            yield f'data: {{"type":"error","content":"{error_msg}"}}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Отключаем буферизацию для nginx
        },
    )


@router.get("/chat/history", response_model=list[ChatMessageResponse])
async def get_history(
    session_id: Annotated[str, Query(description="ID сессии пользователя", min_length=1)],
    web_chat_handler: WebChatHandler = Depends(get_web_chat_handler),  # noqa: B008
) -> list[ChatMessageResponse]:
    """Получить историю чата для session_id.

    Args:
        session_id: ID сессии пользователя (из localStorage)
        web_chat_handler: Инжектируемый обработчик веб-чата

    Returns:
        list[ChatMessageResponse]: Список сообщений из истории

    Raises:
        HTTPException: При ошибке получения истории
    """
    try:
        messages = await web_chat_handler.get_history(session_id)

        # Преобразуем в response модель
        return [
            ChatMessageResponse(
                role=msg["role"],
                content=msg["content"],
                created_at=msg.get("created_at", ""),
            )
            for msg in messages
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch chat history: {e!s}",
        ) from e
