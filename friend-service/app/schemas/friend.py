from pydantic import BaseModel
from datetime import datetime


class SendRequestRequest(BaseModel):
    receiver_id: int


class FriendshipResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime


class FriendResponse(BaseModel):
    user_id: int
    friendship_id: int