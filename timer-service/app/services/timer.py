import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from aiokafka import AIOKafkaProducer

from app.models.timer import Session
from app.schemas.timer import StartSessionRequest
from app.core.config import settings


async def start_session(user_id: int, data: StartSessionRequest, db: AsyncSession) -> Session:
    result = await db.execute(
        select(Session).where(
            Session.user_id == user_id,
            Session.ended_at == None
        )
    )
    active_session = result.scalar_one_or_none()

    if active_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active session"
        )

    session = Session(
        user_id=user_id,
        game_id=data.game_id,
        game_name=data.game_name,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def stop_session(user_id: int, db: AsyncSession) -> Session:
    result = await db.execute(
        select(Session).where(
            Session.user_id == user_id,
            Session.ended_at == None
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )

    now = datetime.now(timezone.utc)
    session.ended_at = now
    session.duration_minutes = int(
        (now - session.started_at.replace(tzinfo=timezone.utc)).total_seconds() / 60
    )

    await db.commit()
    await db.refresh(session)

    await publish_session_completed(session)

    return session


async def get_active_session(user_id: int, db: AsyncSession) -> Session:
    result = await db.execute(
        select(Session).where(
            Session.user_id == user_id,
            Session.ended_at == None
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )
    return session


async def get_sessions(user_id: int, db: AsyncSession) -> list[Session]:
    result = await db.execute(
        select(Session).where(Session.user_id == user_id)
    )
    return result.scalars().all()


async def publish_session_completed(session: Session) -> None:
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        await producer.start()
        message = {
            "user_id": session.user_id,
            "game_id": session.game_id,
            "game_name": session.game_name,
            "duration_minutes": session.duration_minutes,
        }
        await producer.send(
            "session.completed",
            json.dumps(message).encode("utf-8")
        )
        await producer.stop()
    except Exception as e:
        print(f"Failed to publish to Kafka: {e}")