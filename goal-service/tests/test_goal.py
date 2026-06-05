from unittest.mock import AsyncMock, patch
from app.services.goal import create_goal, update_goals_progress
from app.schemas.goal import CreateGoalRequest


async def test_create_goal(client):
    response = await client.post(
        "/api/v1/goals/",
        json={"game_id": 730, "game_name": "CS2", "target_minutes": 100},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["game_name"] == "CS2"
    assert data["target_minutes"] == 100
    assert data["current_minutes"] == 0
    assert data["is_achieved"] == False


async def test_get_goals(client):
    await client.post(
        "/api/v1/goals/",
        json={"game_id": 730, "game_name": "CS2", "target_minutes": 100},
        headers={"X-User-Id": "1"}
    )
    response = await client.get(
        "/api/v1/goals/",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_update_goals_progress(client, db_session):
    await client.post(
        "/api/v1/goals/",
        json={"game_id": 730, "game_name": "CS2", "target_minutes": 100},
        headers={"X-User-Id": "2"}
    )

    with patch("app.services.goal.publish_goal_achieved", new_callable=AsyncMock):
        await update_goals_progress(
            user_id=2,
            game_id=730,
            duration_minutes=50,
            db=db_session
        )

    response = await client.get(
        "/api/v1/goals/",
        headers={"X-User-Id": "2"}
    )
    assert response.status_code == 200
    assert response.json()[0]["current_minutes"] == 50
    assert response.json()[0]["is_achieved"] == False


async def test_goal_achieved(client, db_session):
    await client.post(
        "/api/v1/goals/",
        json={"game_id": 730, "game_name": "CS2", "target_minutes": 60},
        headers={"X-User-Id": "3"}
    )

    with patch("app.services.goal.publish_goal_achieved", new_callable=AsyncMock):
        await update_goals_progress(
            user_id=3,
            game_id=730,
            duration_minutes=60,
            db=db_session
        )

    response = await client.get(
        "/api/v1/goals/",
        headers={"X-User-Id": "3"}
    )
    assert response.json()[0]["is_achieved"] == True


async def test_internal_report_data(client):
    await client.post(
        "/api/v1/goals/",
        json={"game_id": 730, "game_name": "CS2", "target_minutes": 100},
        headers={"X-User-Id": "4"}
    )
    await client.post(
        "/api/v1/goals/",
        json={"game_id": 570, "game_name": "Dota 2", "target_minutes": 50},
        headers={"X-User-Id": "4"}
    )

    response = await client.get(
        "/api/v1/goals/internal/report-data",
        headers={"X-User-Id": "4"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 2
    assert data["achieved_count"] == 0