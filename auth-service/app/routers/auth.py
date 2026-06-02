from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    LogoutRequest,
)
from app.services.auth import (
    register_user,
    login_user,
    refresh_tokens,
    logout_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(data, db)
    return {"id": user.id, "email": user.email}


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user(data, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest):
    return await refresh_tokens(data.refresh_token)


@router.post("/logout", status_code=200)
async def logout(data: LogoutRequest):
    await logout_user(data.access_token)
    return {"detail": "Successfully logged out"}