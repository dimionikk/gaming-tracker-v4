import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from fastapi import HTTPException, status
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.models.goal import Goal
from app.schemas.goal import CreateGoalRequest
from app.core.config import settings


async def create_goal(user_id: int, data: CreateGoalRequest, db: AsyncSession) -> Goal:
    goal = Goal(
        user_id=user_id,
        game_id=data.game_id,
        game_name=data.game_name,
        target_minutes=data.target_minutes,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


async def get_goals(user_id: int, db: AsyncSession) -> list[Goal]:
    result = await db.execute(
        select(Goal).where(Goal.user_id == user_id)
    )
    return result.scalars().all()


async def get_internal_report_data(user_id: int, db: AsyncSession) -> dict:
    goals = await get_goals(user_id, db)
    achieved_count = sum(1 for g in goals if g.is_achieved)
    return {
        "goals": goals,
        "achieved_count": achieved_count,
        "total_count": len(goals),
    }


async def update_goals_progress(user_id: int, game_id: int, duration_minutes: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(Goal).where(
            Goal.user_id == user_id,
            Goal.game_id == game_id,
            Goal.is_achieved == False,
        )
    )
    goals = result.scalars().all()

    for goal in goals:
        goal.current_minutes += duration_minutes
        if goal.current_minutes >= goal.target_minutes:
            goal.is_achieved = True
            await db.commit()
            await publish_goal_achieved(goal)
        else:
            await db.commit()


async def publish_goal_achieved(goal: Goal) -> None:
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        await producer.start()
        message = {
            "user_id": goal.user_id,
            "game_id": goal.game_id,
            "game_name": goal.game_name,
            "target_minutes": goal.target_minutes,
        }
        await producer.send(
            "goal.achieved",
            json.dumps(message).encode("utf-8")
        )
        await producer.stop()
    except Exception as e:
        print(f"Failed to publish to Kafka: {e}")


async def consume_sessions() -> None:
    for attempt in range(10):
        try:
            consumer = AIOKafkaConsumer(
                "session.completed",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="goal-service",
            )
            await consumer.start()
            break
        except Exception:
            await asyncio.sleep(3 * attempt)
    else:
        print("Failed to connect to Kafka after 10 attempts")
        return

    engine = create_async_engine(settings.GOAL_DB_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async for message in consumer:
            data = json.loads(message.value.decode("utf-8"))
            async with AsyncSessionLocal() as db:
                await update_goals_progress(
                    user_id=data["user_id"],
                    game_id=data["game_id"],
                    duration_minutes=data["duration_minutes"],
                    db=db,
                )
    finally:
        await consumer.stop()
        await engine.dispose()