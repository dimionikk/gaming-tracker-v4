from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.leaderboard import LeaderboardEntryResponse
from app.services.leaderboard import get_top

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.get("/top", response_model=list[LeaderboardEntryResponse])
async def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_top(limit, db)