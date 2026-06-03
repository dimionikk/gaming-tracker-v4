import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from aiokafka import AIOKafkaConsumer

from app.models.stats import GameStats
from app.core.config import settings


async def get_user_stats(user_id: int, db: AsyncSession) -> list[GameStats]:
    result = await db.execute(
        select(GameStats).where(GameStats.user_id == user_id)
    )
    return result.scalars().all()


async def get_internal_report_data(user_id: int, db: AsyncSession) -> dict:
    stats = await get_user_stats(user_id, db)
    total_minutes = sum(s.total_minutes for s in stats)
    return {
        "stats": stats,
        "total_games": len(stats),
        "total_minutes": total_minutes,
    }


async def update_stats(user_id: int, game_id: int, game_name: str, duration_minutes: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(GameStats).where(
            GameStats.user_id == user_id,
            GameStats.game_id == game_id,
        )
    )
    stats = result.scalar_one_or_none()

    if stats:
        stats.total_minutes += duration_minutes
    else:
        stats = GameStats(
            user_id=user_id,
            game_id=game_id,
            game_name=game_name,
            total_minutes=duration_minutes,
        )
        db.add(stats)

    await db.commit()


async def consume_sessions() -> None:
    for attempt in range(10):
        try:
            consumer = AIOKafkaConsumer(
                "session.completed",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="stats-service",
            )
            await consumer.start()
            break
        except Exception:
            await asyncio.sleep(3 * attempt)
    else:
        print("Failed to connect to Kafka after 10 attempts")
        return

    engine = create_async_engine(settings.STATS_DB_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async for message in consumer:
            data = json.loads(message.value.decode("utf-8"))
            async with AsyncSessionLocal() as db:
                await update_stats(
                    user_id=data["user_id"],
                    game_id=data["game_id"],
                    game_name=data["game_name"],
                    duration_minutes=data["duration_minutes"],
                    db=db,
                )
    finally:
        await consumer.stop()
        await engine.dispose()