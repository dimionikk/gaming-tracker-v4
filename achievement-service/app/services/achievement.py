import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from aiokafka import AIOKafkaConsumer

from app.models.achievement import Achievement
from app.core.config import settings


ACHIEVEMENTS = {
    "first_hour": "Зіграв першу годину в будь-яку гру",
    "ten_hours": "Зіграв 10 годин загалом",
    "marathon": "Зіграв 100 годин загалом",
    "first_goal": "Досяг першої цілі",
}


async def get_achievements(user_id: int, db: AsyncSession) -> list[Achievement]:
    result = await db.execute(
        select(Achievement).where(Achievement.user_id == user_id)
    )
    return result.scalars().all()


async def get_internal_report_data(user_id: int, db: AsyncSession) -> dict:
    achievements = await get_achievements(user_id, db)
    return {
        "achievements": achievements,
        "total_count": len(achievements),
    }


async def unlock_achievement(user_id: int, achievement_type: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(Achievement).where(
            Achievement.user_id == user_id,
            Achievement.type == achievement_type,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        return

    achievement = Achievement(
        user_id=user_id,
        type=achievement_type,
        description=ACHIEVEMENTS[achievement_type],
    )
    db.add(achievement)
    await db.commit()


async def check_session_achievements(user_id: int, total_minutes: int, db: AsyncSession) -> None:
    if total_minutes >= 60:
        await unlock_achievement(user_id, "first_hour", db)
    if total_minutes >= 600:
        await unlock_achievement(user_id, "ten_hours", db)
    if total_minutes >= 6000:
        await unlock_achievement(user_id, "marathon", db)


async def consume_events() -> None:
    for attempt in range(10):
        try:
            consumer = AIOKafkaConsumer(
                "session.completed",
                "goal.achieved",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="achievement-service",
            )
            await consumer.start()
            break
        except Exception:
            await asyncio.sleep(3 * attempt)
    else:
        print("Failed to connect to Kafka after 10 attempts")
        return

    engine = create_async_engine(settings.ACHIEVEMENT_DB_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async for message in consumer:
            data = json.loads(message.value.decode("utf-8"))
            topic = message.topic

            async with AsyncSessionLocal() as db:
                if topic == "session.completed":
                    total_minutes = data.get("total_minutes", data["duration_minutes"])
                    await check_session_achievements(
                        user_id=data["user_id"],
                        total_minutes=total_minutes,
                        db=db,
                    )
                elif topic == "goal.achieved":
                    await unlock_achievement(
                        user_id=data["user_id"],
                        achievement_type="first_goal",
                        db=db,
                    )
    finally:
        await consumer.stop()
        await engine.dispose()