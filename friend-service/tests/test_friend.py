from unittest.mock import AsyncMock, patch


async def test_send_request(client):
    response = await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 2},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["sender_id"] == 1
    assert data["receiver_id"] == 2
    assert data["status"] == "pending"


async def test_send_request_to_yourself(client):
    response = await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 1},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 400


async def test_send_duplicate_request(client):
    await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 2},
        headers={"X-User-Id": "1"}
    )
    response = await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 2},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 400


async def test_accept_request(client):
    response = await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 2},
        headers={"X-User-Id": "1"}
    )
    friendship_id = response.json()["id"]

    with patch("app.services.friend.publish_friend_accepted", new_callable=AsyncMock):
        response = await client.post(
            f"/api/v1/friends/accept/{friendship_id}",
            headers={"X-User-Id": "2"}
        )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


async def test_reject_request(client):
    response = await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 2},
        headers={"X-User-Id": "1"}
    )
    friendship_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/friends/reject/{friendship_id}",
        headers={"X-User-Id": "2"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


async def test_get_friends(client):
    response = await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 2},
        headers={"X-User-Id": "1"}
    )
    friendship_id = response.json()["id"]

    with patch("app.services.friend.publish_friend_accepted", new_callable=AsyncMock):
        await client.post(
            f"/api/v1/friends/accept/{friendship_id}",
            headers={"X-User-Id": "2"}
        )

    response = await client.get(
        "/api/v1/friends/",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_incoming_requests(client):
    await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 2},
        headers={"X-User-Id": "1"}
    )
    response = await client.get(
        "/api/v1/friends/incoming",
        headers={"X-User-Id": "2"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_outgoing_requests(client):
    await client.post(
        "/api/v1/friends/request",
        json={"receiver_id": 2},
        headers={"X-User-Id": "1"}
    )
    response = await client.get(
        "/api/v1/friends/outgoing",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1