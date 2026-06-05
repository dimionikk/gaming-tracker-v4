import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from redis.asyncio import Redis

from app.models.chat import Message
from app.core.config import settings


async def save_message(sender_id: int, receiver_id: int, content: str, db: AsyncSession) -> Message:
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_history(user_id: int, other_user_id: int, db: AsyncSession) -> list[Message]:
    result = await db.execute(
        select(Message).where(
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == user_id),
            )
        ).order_by(Message.created_at.asc())
    )
    return result.scalars().all()


async def publish_message(sender_id: int, receiver_id: int, content: str) -> None:
    redis = Redis.from_url(settings.REDIS_URL)
    channel = f"chat:{min(sender_id, receiver_id)}:{max(sender_id, receiver_id)}"
    message = json.dumps({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "content": content,
    })
    await redis.publish(channel, message)
    await redis.aclose()


async def subscribe_to_channel(sender_id: int, receiver_id: int) -> tuple:
    redis = Redis.from_url(settings.REDIS_URL)
    channel = f"chat:{min(sender_id, receiver_id)}:{max(sender_id, receiver_id)}"
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    return redis, pubsub