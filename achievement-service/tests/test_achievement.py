from unittest.mock import AsyncMock, patch
from app.services.achievement import unlock_achievement, check_session_achievements


async def test_empty_achievements(client):
    response = await client.get(
        "/api/v1/achievements/",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_unlock_achievement(client, db_session):
    await unlock_achievement(
        user_id=1,
        achievement_type="first_hour",
        db=db_session
    )

    response = await client.get(
        "/api/v1/achievements/",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "first_hour"


async def test_no_duplicate_achievement(client, db_session):
    await unlock_achievement(user_id=2, achievement_type="first_hour", db=db_session)
    await unlock_achievement(user_id=2, achievement_type="first_hour", db=db_session)

    response = await client.get(
        "/api/v1/achievements/",
        headers={"X-User-Id": "2"}
    )
    assert len(response.json()) == 1


async def test_check_session_achievements(client, db_session):
    await check_session_achievements(
        user_id=3,
        total_minutes=60,
        db=db_session
    )

    response = await client.get(
        "/api/v1/achievements/",
        headers={"X-User-Id": "3"}
    )
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "first_hour"


async def test_internal_report_data(client, db_session):
    await unlock_achievement(user_id=4, achievement_type="first_hour", db=db_session)
    await unlock_achievement(user_id=4, achievement_type="first_goal", db=db_session)

    response = await client.get(
        "/api/v1/achievements/internal/report-data",
        headers={"X-User-Id": "4"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 2