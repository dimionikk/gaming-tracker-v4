from pydantic import BaseModel
from datetime import datetime


class AchievementResponse(BaseModel):
    id: int
    user_id: int
    type: str
    description: str
    created_at: datetime


class InternalReportData(BaseModel):
    achievements: list[AchievementResponse]
    total_count: int