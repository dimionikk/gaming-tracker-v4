from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.goal import CreateGoalRequest, GoalResponse, InternalReportData
from app.services.goal import create_goal, get_goals, get_internal_report_data

router = APIRouter(prefix="/goals", tags=["goals"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.post("/", status_code=201, response_model=GoalResponse)
async def create_new_goal(
    data: CreateGoalRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await create_goal(user_id, data, db)


@router.get("/", response_model=list[GoalResponse])
async def get_user_goals(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_goals(user_id, db)


@router.get("/internal/report-data", response_model=InternalReportData)
async def internal_report_data(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_internal_report_data(user_id, db)