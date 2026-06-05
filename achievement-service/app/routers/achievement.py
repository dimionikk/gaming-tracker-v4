from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.achievement import AchievementResponse, InternalReportData
from app.services.achievement import get_achievements, get_internal_report_data

router = APIRouter(prefix="/achievements", tags=["achievements"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.get("/", response_model=list[AchievementResponse])
async def get_user_achievements(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_achievements(user_id, db)


@router.get("/internal/report-data", response_model=InternalReportData)
async def internal_report_data(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_internal_report_data(user_id, db)