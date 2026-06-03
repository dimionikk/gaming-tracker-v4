from unittest.mock import AsyncMock, patch
from app.services.stats import update_stats


async def test_get_empty_stats(client):
    response = await client.get(
        "/api/v1/stats/games",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_update_and_get_stats(client, db_session):
    await update_stats(
        user_id=1,
        game_id=730,
        game_name="CS2",
        duration_minutes=60,
        db=db_session
    )

    response = await client.get(
        "/api/v1/stats/games",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["game_name"] == "CS2"
    assert data[0]["total_minutes"] == 60


async def test_update_stats_twice(client, db_session):
    await update_stats(
        user_id=2,
        game_id=730,
        game_name="CS2",
        duration_minutes=60,
        db=db_session
    )
    await update_stats(
        user_id=2,
        game_id=730,
        game_name="CS2",
        duration_minutes=30,
        db=db_session
    )

    response = await client.get(
        "/api/v1/stats/games",
        headers={"X-User-Id": "2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["total_minutes"] == 90


async def test_internal_report_data(client, db_session):
    await update_stats(
        user_id=3,
        game_id=730,
        game_name="CS2",
        duration_minutes=60,
        db=db_session
    )
    await update_stats(
        user_id=3,
        game_id=570,
        game_name="Dota 2",
        duration_minutes=30,
        db=db_session
    )

    response = await client.get(
        "/api/v1/stats/internal/report-data",
        headers={"X-User-Id": "3"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_games"] == 2
    assert data["total_minutes"] == 90