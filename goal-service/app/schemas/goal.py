from pydantic import BaseModel
from datetime import datetime


class CreateGoalRequest(BaseModel):
    game_id: int
    game_name: str
    target_minutes: int


class GoalResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    game_name: str
    target_minutes: int
    current_minutes: int
    is_achieved: bool
    created_at: datetime


class InternalReportData(BaseModel):
    goals: list[GoalResponse]
    achieved_count: int
    total_count: int