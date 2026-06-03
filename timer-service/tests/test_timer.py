from unittest.mock import AsyncMock, patch


async def test_start_session(client):
    response = await client.post(
        "/api/v1/timer/start",
        json={"game_id": 730, "game_name": "CS2"},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["game_name"] == "CS2"
    assert data["user_id"] == 1
    assert data["ended_at"] is None


async def test_start_session_duplicate(client):
    await client.post(
        "/api/v1/timer/start",
        json={"game_id": 730, "game_name": "CS2"},
        headers={"X-User-Id": "2"}
    )
    response = await client.post(
        "/api/v1/timer/start",
        json={"game_id": 730, "game_name": "CS2"},
        headers={"X-User-Id": "2"}
    )
    assert response.status_code == 400


async def test_stop_session(client):
    with patch("app.services.timer.publish_session_completed", new_callable=AsyncMock):
        await client.post(
            "/api/v1/timer/start",
            json={"game_id": 730, "game_name": "CS2"},
            headers={"X-User-Id": "3"}
        )
        response = await client.post(
            "/api/v1/timer/stop",
            headers={"X-User-Id": "3"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["ended_at"] is not None
    assert data["duration_minutes"] is not None


async def test_stop_session_no_active(client):
    response = await client.post(
        "/api/v1/timer/stop",
        headers={"X-User-Id": "999"}
    )
    assert response.status_code == 404


async def test_get_active_session(client):
    await client.post(
        "/api/v1/timer/start",
        json={"game_id": 730, "game_name": "CS2"},
        headers={"X-User-Id": "4"}
    )
    response = await client.get(
        "/api/v1/timer/active",
        headers={"X-User-Id": "4"}
    )
    assert response.status_code == 200
    assert response.json()["game_name"] == "CS2"


async def test_get_sessions(client):
    with patch("app.services.timer.publish_session_completed", new_callable=AsyncMock):
        await client.post(
            "/api/v1/timer/start",
            json={"game_id": 730, "game_name": "CS2"},
            headers={"X-User-Id": "5"}
        )
        await client.post(
            "/api/v1/timer/stop",
            headers={"X-User-Id": "5"}
        )
    response = await client.get(
        "/api/v1/timer/sessions",
        headers={"X-User-Id": "5"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1