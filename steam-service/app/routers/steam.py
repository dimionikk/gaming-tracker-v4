from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.steam import (
    ConnectSteamRequest,
    SteamAccountResponse,
    GameResponse,
    SyncResponse,
)
from app.services.steam import (
    connect_steam,
    get_steam_account,
    sync_games,
    get_games,
)

router = APIRouter(prefix="/steam", tags=["steam"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.post("/connect", status_code=201, response_model=SteamAccountResponse)
async def connect_steam_account(
    data: ConnectSteamRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await connect_steam(user_id, data, db)


@router.get("/account", response_model=SteamAccountResponse)
async def get_account(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_steam_account(user_id, db)


@router.post("/sync", response_model=SyncResponse)
async def sync_steam_games(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await sync_games(user_id, db)


@router.get("/games", response_model=list[GameResponse])
async def get_steam_games(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_games(user_id, db)