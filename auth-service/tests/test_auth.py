import pytest


async def test_register(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@gmail.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@gmail.com"
    assert "id" in data


async def test_register_duplicate_email(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@gmail.com", "password": "password123"}
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@gmail.com", "password": "password123"}
    )
    assert response.status_code == 400


async def test_login(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@gmail.com", "password": "password123"}
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@gmail.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_wrong_password(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@gmail.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


async def test_refresh(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@gmail.com", "password": "password123"}
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@gmail.com", "password": "password123"}
    )
    refresh_token = login.json()["refresh_token"]
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_logout(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "logout@gmail.com", "password": "password123"}
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "logout@gmail.com", "password": "password123"}
    )
    access_token = login.json()["access_token"]
    response = await client.post(
        "/api/v1/auth/logout",
        json={"access_token": access_token}
    )
    assert response.status_code == 200