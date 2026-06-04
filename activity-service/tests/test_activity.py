import asyncio
from app.services.activity import create_activity


async def test_empty_feed(client):
    response = await client.get(
        "/api/v1/activity/feed",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_create_and_get_feed(client, db_session):
    await create_activity(
        user_id=1,
        activity_type="session_completed",
        payload={"game_name": "CS2", "duration_minutes": 60},
        db=db_session
    )

    response = await client.get(
        "/api/v1/activity/feed",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "session_completed"


async def test_feed_order(client, db_session):
    await create_activity(
        user_id=2,
        activity_type="session_completed",
        payload={"game_name": "CS2", "duration_minutes": 60},
        db=db_session
    )
    await asyncio.sleep(0.01)
    await create_activity(
        user_id=2,
        activity_type="friend_accepted",
        payload={"friend_id": 3},
        db=db_session
    )

    response = await client.get(
        "/api/v1/activity/feed",
        headers={"X-User-Id": "2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["type"] == "friend_accepted"


async def test_feed_only_own(client, db_session):
    await create_activity(
        user_id=3,
        activity_type="session_completed",
        payload={"game_name": "CS2", "duration_minutes": 60},
        db=db_session
    )
    await create_activity(
        user_id=4,
        activity_type="session_completed",
        payload={"game_name": "Dota 2", "duration_minutes": 30},
        db=db_session
    )

    response = await client.get(
        "/api/v1/activity/feed",
        headers={"X-User-Id": "3"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1