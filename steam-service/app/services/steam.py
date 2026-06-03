import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select, delete
from app.models.steam import SteamAccount, Game
from app.schemas.steam import ConnectSteamRequest
from app.core.config import settings


async def connect_steam(user_id: int, data: ConnectSteamRequest, db: AsyncSession) -> SteamAccount:
    result = await db.execute(
        select(SteamAccount).where(SteamAccount.user_id == user_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Steam account already connected"
        )

    account = SteamAccount(
        user_id=user_id,
        steam_id=data.steam_id,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def get_steam_account(user_id: int, db: AsyncSession) -> SteamAccount:
    result = await db.execute(
        select(SteamAccount).where(SteamAccount.user_id == user_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Steam account not connected"
        )
    return account


async def sync_games(user_id: int, db: AsyncSession) -> dict:
    account = await get_steam_account(user_id, db)

    client = httpx.AsyncClient()
    response = await client.get(
        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/",
        params={
            "key": settings.STEAM_API_KEY,
            "steamid": account.steam_id,
            "include_appinfo": 1,
            "include_played_free_games": 1,
        }
    )
    await client.aclose()

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch games from Steam"
        )

    data = response.json()
    steam_games = data.get("response", {}).get("games", [])

    await db.execute(
        delete(Game).where(Game.user_id == user_id)
    )

    games = []
    for g in steam_games:
        game = Game(
            user_id=user_id,
            steam_id=account.steam_id,
            app_id=g["appid"],
            name=g.get("name", "Unknown"),
            playtime_forever=g.get("playtime_forever", 0),
        )
        db.add(game)
        games.append(game)

    await db.commit()
    for game in games:
        await db.refresh(game)

    return {"synced": len(games), "games": games}


async def get_games(user_id: int, db: AsyncSession) -> list[Game]:
    await get_steam_account(user_id, db)

    result = await db.execute(
        select(Game).where(Game.user_id == user_id)
    )
    return result.scalars().all()