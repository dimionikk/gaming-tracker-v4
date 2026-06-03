from unittest.mock import AsyncMock, MagicMock, patch

async def test_connect_steam(client):
    response = await client.post(
        "/api/v1/steam/connect",
        json={"steam_id": "76561198000000001"},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["steam_id"] == "76561198000000001"
    assert data["user_id"] == 1


async def test_connect_steam_duplicate(client):
    await client.post(
        "/api/v1/steam/connect",
        json={"steam_id": "76561198000000002"},
        headers={"X-User-Id": "2"}
    )
    response = await client.post(
        "/api/v1/steam/connect",
        json={"steam_id": "76561198000000002"},
        headers={"X-User-Id": "2"}
    )
    assert response.status_code == 400


async def test_get_account(client):
    await client.post(
        "/api/v1/steam/connect",
        json={"steam_id": "76561198000000003"},
        headers={"X-User-Id": "3"}
    )
    response = await client.get(
        "/api/v1/steam/account",
        headers={"X-User-Id": "3"}
    )
    assert response.status_code == 200
    assert response.json()["steam_id"] == "76561198000000003"


async def test_get_account_not_found(client):
    response = await client.get(
        "/api/v1/steam/account",
        headers={"X-User-Id": "999"}
    )
    assert response.status_code == 404


async def test_sync_games(client):
    await client.post(
        "/api/v1/steam/connect",
        json={"steam_id": "76561198000000004"},
        headers={"X-User-Id": "4"}
    )

    fake_games_data = {
        "response": {
            "game_count": 2,
            "games": [
                {"appid": 730, "name": "CS2", "playtime_forever": 1200},
                {"appid": 570, "name": "Dota 2", "playtime_forever": 500},
            ]
        }
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = fake_games_data

    async def mock_get(*args, **kwargs):
        return mock_response

    with patch("app.services.steam.httpx.AsyncClient") as mock_client_class:
        mock_instance = MagicMock()
        mock_instance.get = mock_get
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        response = await client.post(
            "/api/v1/steam/sync",
            headers={"X-User-Id": "4"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["synced"] == 2
    assert len(data["games"]) == 2


async def test_get_games(client):
    await client.post(
        "/api/v1/steam/connect",
        json={"steam_id": "76561198000000005"},
        headers={"X-User-Id": "5"}
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": {
            "games": [
                {"appid": 730, "name": "CS2", "playtime_forever": 1200},
            ]
        }
    }

    async def mock_get(*args, **kwargs):
        return mock_response

    with patch("app.services.steam.httpx.AsyncClient") as mock_client_class:
        mock_instance = MagicMock()
        mock_instance.get = mock_get
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        await client.post(
            "/api/v1/steam/sync",
            headers={"X-User-Id": "5"}
        )

    response = await client.get(
        "/api/v1/steam/games",
        headers={"X-User-Id": "5"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1