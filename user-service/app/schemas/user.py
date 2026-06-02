from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    username: str
    bio: str | None
    avatar_url: str | None


class UserProfileUpdate(BaseModel):
    username: str | None = None
    bio: str | None = None
    avatar_url: str | None = None