from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.stats import GameStatsResponse, InternalReportData
from app.services.stats import get_user_stats, get_internal_report_data

router = APIRouter(prefix="/stats", tags=["stats"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.get("/games", response_model=list[GameStatsResponse])
async def get_games_stats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_user_stats(user_id, db)


@router.get("/internal/report-data", response_model=InternalReportData)
async def internal_report_data(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_internal_report_data(user_id, db)