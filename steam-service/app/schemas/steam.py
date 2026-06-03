from pydantic import BaseModel
from datetime import datetime


class ConnectSteamRequest(BaseModel):
    steam_id: str


class SteamAccountResponse(BaseModel):
    id: int
    user_id: int
    steam_id: str
    display_name: str | None
    connected_at: datetime


class GameResponse(BaseModel):
    id: int
    user_id: int
    app_id: int
    name: str
    playtime_forever: int


class SyncResponse(BaseModel):
    synced: int
    games: list[GameResponse]