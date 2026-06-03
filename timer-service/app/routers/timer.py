from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.timer import StartSessionRequest, SessionResponse, StopSessionResponse
from app.services.timer import start_session, stop_session, get_active_session, get_sessions

router = APIRouter(prefix="/timer", tags=["timer"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.post("/start", status_code=201, response_model=SessionResponse)
async def start(
    data: StartSessionRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await start_session(user_id, data, db)


@router.post("/stop", response_model=StopSessionResponse)
async def stop(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await stop_session(user_id, db)


@router.get("/active", response_model=SessionResponse)
async def active(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_active_session(user_id, db)


@router.get("/sessions", response_model=list[SessionResponse])
async def sessions(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_sessions(user_id, db)