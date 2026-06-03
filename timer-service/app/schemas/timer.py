from pydantic import BaseModel
from datetime import datetime


class StartSessionRequest(BaseModel):
    game_id: int
    game_name: str


class SessionResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    game_name: str
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int | None


class StopSessionResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    game_name: str
    started_at: datetime
    ended_at: datetime
    duration_minutes: int