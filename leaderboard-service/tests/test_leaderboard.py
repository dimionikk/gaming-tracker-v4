from app.services.leaderboard import update_leaderboard


async def test_empty_leaderboard(client):
    response = await client.get(
        "/api/v1/leaderboard/top",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_update_and_get_top(client, db_session):
    await update_leaderboard(user_id=1, duration_minutes=120, db=db_session)
    await update_leaderboard(user_id=2, duration_minutes=60, db=db_session)

    response = await client.get(
        "/api/v1/leaderboard/top",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["user_id"] == 1
    assert data[0]["total_minutes"] == 120


async def test_update_twice(client, db_session):
    await update_leaderboard(user_id=3, duration_minutes=60, db=db_session)
    await update_leaderboard(user_id=3, duration_minutes=30, db=db_session)

    response = await client.get(
        "/api/v1/leaderboard/top",
        headers={"X-User-Id": "3"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["total_minutes"] == 90


async def test_limit(client, db_session):
    await update_leaderboard(user_id=1, duration_minutes=100, db=db_session)
    await update_leaderboard(user_id=2, duration_minutes=80, db=db_session)
    await update_leaderboard(user_id=3, duration_minutes=60, db=db_session)

    response = await client.get(
        "/api/v1/leaderboard/top?limit=2",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2