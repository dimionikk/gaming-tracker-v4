from pydantic import BaseModel
from datetime import datetime


class LeaderboardEntryResponse(BaseModel):
    id: int
    user_id: int
    total_minutes: int
    updated_at: datetime