import pytest


async def test_create_profile(client):
    response = await client.post(
        "/api/v1/users/me",
        params={"username": "testuser"},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["user_id"] == 1


async def test_get_profile(client):
    await client.post(
        "/api/v1/users/me",
        params={"username": "testuser2"},
        headers={"X-User-Id": "2"}
    )
    response = await client.get(
        "/api/v1/users/me",
        headers={"X-User-Id": "2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser2"


async def test_update_profile(client):
    await client.post(
        "/api/v1/users/me",
        params={"username": "testuser3"},
        headers={"X-User-Id": "3"}
    )
    response = await client.put(
        "/api/v1/users/me",
        json={"bio": "Hello world"},
        headers={"X-User-Id": "3"}
    )
    assert response.status_code == 200
    assert response.json()["bio"] == "Hello world"


async def test_get_profile_not_found(client):
    response = await client.get(
        "/api/v1/users/me",
        headers={"X-User-Id": "999"}
    )
    assert response.status_code == 404


async def test_get_other_user_profile(client):
    await client.post(
        "/api/v1/users/me",
        params={"username": "testuser4"},
        headers={"X-User-Id": "4"}
    )
    response = await client.get("/api/v1/users/4")
    assert response.status_code == 200
    assert response.json()["user_id"] == 4