from pydantic import BaseModel
from datetime import datetime


class GameStatsResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    game_name: str
    total_minutes: int
    updated_at: datetime


class InternalReportData(BaseModel):
    stats: list[GameStatsResponse]
    total_games: int
    total_minutes: int