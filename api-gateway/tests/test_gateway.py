import pytest
from unittest.mock import AsyncMock, patch


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_auth_route_without_token(client):
    with patch("app.routers.proxy.http_client") as mock_client:
        mock_response = AsyncMock()
        mock_response.content = b'{"detail": "Not found"}'
        mock_response.status_code = 404
        mock_response.headers = {"content-type": "application/json"}
        mock_client.request = AsyncMock(return_value=mock_response)

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@gmail.com", "password": "password123"}
        )
        assert response.status_code == 404


async def test_users_route_without_token(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_users_route_with_invalid_token(client):
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401