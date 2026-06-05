import json
from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.chat import MessageResponse
from app.services.chat import save_message, get_history, publish_message, subscribe_to_channel

router = APIRouter(prefix="/chat", tags=["chat"])


async def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )


@router.websocket("/ws/{receiver_id}")
async def websocket_chat(
    websocket: WebSocket,
    receiver_id: int,
    db: AsyncSession = Depends(get_db),
):
    user_id_header = websocket.headers.get("x-user-id")
    if not user_id_header:
        await websocket.close(code=1008)
        return
    try:
        user_id = int(user_id_header)
    except ValueError:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    redis, pubsub = await subscribe_to_channel(user_id, receiver_id)

    try:
        while True:
            data = await websocket.receive_text()
            content = json.loads(data).get("content", "")

            if content:
                await save_message(user_id, receiver_id, content, db)
                await publish_message(user_id, receiver_id, content)

            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if message and message["type"] == "message":
                await websocket.send_text(message["data"].decode("utf-8"))

    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe()
        await redis.aclose()


@router.get("/history/{other_user_id}", response_model=list[MessageResponse])
async def chat_history(
    other_user_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_history(user_id, other_user_id, db)