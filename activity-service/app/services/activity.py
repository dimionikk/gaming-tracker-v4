import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from aiokafka import AIOKafkaConsumer

from app.models.activity import Activity
from app.core.config import settings


async def get_feed(user_id: int, db: AsyncSession) -> list[Activity]:
    result = await db.execute(
        select(Activity)
        .where(Activity.user_id == user_id)
        .order_by(Activity.created_at.desc())
    )
    return result.scalars().all()


async def create_activity(user_id: int, activity_type: str, payload: dict, db: AsyncSession) -> Activity:
    activity = Activity(
        user_id=user_id,
        type=activity_type,
        payload=json.dumps(payload),
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def consume_events() -> None:
    for attempt in range(10):
        try:
            consumer = AIOKafkaConsumer(
                "session.completed",
                "friend.accepted",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="activity-service",
            )
            await consumer.start()
            break
        except Exception:
            await asyncio.sleep(3 * attempt)
    else:
        print("Failed to connect to Kafka after 10 attempts")
        return

    engine = create_async_engine(settings.ACTIVITY_DB_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async for message in consumer:
            data = json.loads(message.value.decode("utf-8"))
            topic = message.topic

            async with AsyncSessionLocal() as db:
                if topic == "session.completed":
                    await create_activity(
                        user_id=data["user_id"],
                        activity_type="session_completed",
                        payload={
                            "game_name": data["game_name"],
                            "duration_minutes": data["duration_minutes"],
                        },
                        db=db,
                    )
                elif topic == "friend.accepted":
                    await create_activity(
                        user_id=data["sender_id"],
                        activity_type="friend_accepted",
                        payload={"friend_id": data["receiver_id"]},
                        db=db,
                    )
                    await create_activity(
                        user_id=data["receiver_id"],
                        activity_type="friend_accepted",
                        payload={"friend_id": data["sender_id"]},
                        db=db,
                    )
    finally:
        await consumer.stop()
        await engine.dispose()