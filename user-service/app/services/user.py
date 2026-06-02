from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import UserProfile
from app.schemas.user import UserProfileUpdate


async def get_profile(user_id: int, db: AsyncSession) -> UserProfile:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


async def update_profile(
    user_id: int, data: UserProfileUpdate, db: AsyncSession
) -> UserProfile:
    profile = await get_profile(user_id, db)

    if data.username is not None:
        profile.username = data.username
    if data.bio is not None:
        profile.bio = data.bio
    if data.avatar_url is not None:
        profile.avatar_url = data.avatar_url

    await db.commit()
    await db.refresh(profile)
    return profile


async def create_profile(user_id: int, username: str, db: AsyncSession) -> UserProfile:
    profile = UserProfile(user_id=user_id, username=username)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile