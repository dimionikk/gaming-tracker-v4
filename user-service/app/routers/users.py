from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.schemas.user import UserProfileResponse, UserProfileUpdate
from app.services.user import get_profile, update_profile, create_profile

router = APIRouter(prefix="/users", tags=["users"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.post("/me", status_code=201, response_model=UserProfileResponse)
async def create_my_profile(
    username: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await create_profile(user_id, username, db)


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_profile(user_id, db)


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await update_profile(user_id, data, db)


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_profile(user_id, db)