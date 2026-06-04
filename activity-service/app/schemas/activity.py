from pydantic import BaseModel
from datetime import datetime


class ActivityResponse(BaseModel):
    id: int
    user_id: int
    type: str
    payload: str
    created_at: datetime