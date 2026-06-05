from unittest.mock import AsyncMock, MagicMock, patch
from app.services.chat import save_message, get_history


async def test_save_and_get_history(client, db_session):
    await save_message(
        sender_id=1,
        receiver_id=2,
        content="Привіт!",
        db=db_session
    )
    await save_message(
        sender_id=2,
        receiver_id=1,
        content="Привіт! Як справи?",
        db=db_session
    )

    response = await client.get(
        "/api/v1/chat/history/2",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] == "Привіт!"
    assert data[1]["content"] == "Привіт! Як справи?"


async def test_empty_history(client):
    response = await client.get(
        "/api/v1/chat/history/2",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_history_both_directions(client, db_session):
    await save_message(sender_id=1, receiver_id=2, content="Повідомлення 1", db=db_session)
    await save_message(sender_id=2, receiver_id=1, content="Повідомлення 2", db=db_session)
    await save_message(sender_id=1, receiver_id=2, content="Повідомлення 3", db=db_session)

    response = await client.get(
        "/api/v1/chat/history/2",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


async def test_websocket_chat():
    mock_websocket = AsyncMock()
    mock_websocket.headers = {"x-user-id": "1"}
    mock_websocket.receive_text = AsyncMock(side_effect=[
        '{"content": "Привіт!"}',
        Exception("disconnect")
    ])

    mock_pubsub = AsyncMock()
    mock_pubsub.get_message = AsyncMock(return_value=None)
    mock_pubsub.unsubscribe = AsyncMock()

    mock_redis = AsyncMock()
    mock_redis.aclose = AsyncMock()

    with patch("app.routers.chat.save_message", new_callable=AsyncMock) as mock_save, \
         patch("app.routers.chat.publish_message", new_callable=AsyncMock), \
         patch("app.routers.chat.subscribe_to_channel", new_callable=AsyncMock) as mock_subscribe:

        mock_subscribe.return_value = (mock_redis, mock_pubsub)

        from app.routers.chat import websocket_chat
        try:
            await websocket_chat(mock_websocket, receiver_id=2, db=AsyncMock())
        except Exception:
            pass

        mock_save.assert_called_once()