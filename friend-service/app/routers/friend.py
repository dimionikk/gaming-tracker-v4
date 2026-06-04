from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.friend import SendRequestRequest, FriendshipResponse, FriendResponse
from app.services.friend import (
    send_request,
    accept_request,
    reject_request,
    get_friends,
    get_incoming_requests,
    get_outgoing_requests,
)

router = APIRouter(prefix="/friends", tags=["friends"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.post("/request", status_code=201, response_model=FriendshipResponse)
async def send_friend_request(
    data: SendRequestRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await send_request(user_id, data, db)


@router.post("/accept/{friendship_id}", response_model=FriendshipResponse)
async def accept_friend_request(
    friendship_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await accept_request(user_id, friendship_id, db)


@router.post("/reject/{friendship_id}", response_model=FriendshipResponse)
async def reject_friend_request(
    friendship_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await reject_request(user_id, friendship_id, db)


@router.get("/", response_model=list[FriendResponse])
async def friends_list(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_friends(user_id, db)


@router.get("/incoming", response_model=list[FriendshipResponse])
async def incoming_requests(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_incoming_requests(user_id, db)


@router.get("/outgoing", response_model=list[FriendshipResponse])
async def outgoing_requests(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_outgoing_requests(user_id, db)