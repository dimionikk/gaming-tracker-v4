import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from fastapi import HTTPException, status
from aiokafka import AIOKafkaProducer

from app.models.friend import Friendship
from app.schemas.friend import SendRequestRequest
from app.core.config import settings


async def send_request(user_id: int, data: SendRequestRequest, db: AsyncSession) -> Friendship:
    if user_id == data.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send friend request to yourself"
        )

    result = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.sender_id == user_id, Friendship.receiver_id == data.receiver_id),
                and_(Friendship.sender_id == data.receiver_id, Friendship.receiver_id == user_id),
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friendship already exists"
        )

    friendship = Friendship(
        sender_id=user_id,
        receiver_id=data.receiver_id,
    )
    db.add(friendship)
    await db.commit()
    await db.refresh(friendship)
    return friendship


async def accept_request(user_id: int, friendship_id: int, db: AsyncSession) -> Friendship:
    result = await db.execute(
        select(Friendship).where(
            Friendship.id == friendship_id,
            Friendship.receiver_id == user_id,
            Friendship.status == "pending",
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )

    friendship.status = "accepted"
    await db.commit()
    await db.refresh(friendship)

    await publish_friend_accepted(friendship)

    return friendship


async def reject_request(user_id: int, friendship_id: int, db: AsyncSession) -> Friendship:
    result = await db.execute(
        select(Friendship).where(
            Friendship.id == friendship_id,
            Friendship.receiver_id == user_id,
            Friendship.status == "pending",
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )

    friendship.status = "rejected"
    await db.commit()
    await db.refresh(friendship)
    return friendship


async def get_friends(user_id: int, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Friendship).where(
            or_(
                Friendship.sender_id == user_id,
                Friendship.receiver_id == user_id,
            ),
            Friendship.status == "accepted",
        )
    )
    friendships = result.scalars().all()

    friends = []
    for f in friendships:
        friend_id = f.receiver_id if f.sender_id == user_id else f.sender_id
        friends.append({"user_id": friend_id, "friendship_id": f.id})
    return friends


async def get_incoming_requests(user_id: int, db: AsyncSession) -> list[Friendship]:
    result = await db.execute(
        select(Friendship).where(
            Friendship.receiver_id == user_id,
            Friendship.status == "pending",
        )
    )
    return result.scalars().all()


async def get_outgoing_requests(user_id: int, db: AsyncSession) -> list[Friendship]:
    result = await db.execute(
        select(Friendship).where(
            Friendship.sender_id == user_id,
            Friendship.status == "pending",
        )
    )
    return result.scalars().all()


async def publish_friend_accepted(friendship: Friendship) -> None:
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        await producer.start()
        message = {
            "sender_id": friendship.sender_id,
            "receiver_id": friendship.receiver_id,
        }
        await producer.send(
            "friend.accepted",
            json.dumps(message).encode("utf-8")
        )
        await producer.stop()
    except Exception as e:
        print(f"Failed to publish to Kafka: {e}")