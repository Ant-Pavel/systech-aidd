"""API endpoints для дашборда."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.app import get_stat_collector
from src.api.models import DashboardStats
from src.api.protocols import StatCollectorProtocol

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
