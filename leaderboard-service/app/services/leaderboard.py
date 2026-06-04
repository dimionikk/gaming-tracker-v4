import json
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from aiokafka import AIOKafkaConsumer

from app.models.leaderboard import LeaderboardEntry
from app.core.config import settings


async def get_top(limit: int, db: AsyncSession) -> list[LeaderboardEntry]:
    result = await db.execute(
        select(LeaderboardEntry)
        .order_by(LeaderboardEntry.total_minutes.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def update_leaderboard(user_id: int, duration_minutes: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id)
    )
    entry = result.scalar_one_or_none()

    if entry:
        entry.total_minutes += duration_minutes
        entry.updated_at = datetime.now(timezone.utc)
    else:
        entry = LeaderboardEntry(
            user_id=user_id,
            total_minutes=duration_minutes,
        )
        db.add(entry)

    await db.commit()


async def consume_sessions() -> None:
    for attempt in range(10):
        try:
            consumer = AIOKafkaConsumer(
                "session.completed",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="leaderboard-service",
            )
            await consumer.start()
            break
        except Exception:
            await asyncio.sleep(3 * attempt)
    else:
        print("Failed to connect to Kafka after 10 attempts")
        return

    engine = create_async_engine(settings.LEADERBOARD_DB_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async for message in consumer:
            data = json.loads(message.value.decode("utf-8"))
            async with AsyncSessionLocal() as db:
                await update_leaderboard(
                    user_id=data["user_id"],
                    duration_minutes=data["duration_minutes"],
                    db=db,
                )
    finally:
        await consumer.stop()
        await engine.dispose()