import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

def test_ws_authorized_connection(client: TestClient, db, normal_user_token_headers, test_channel):
    token = normal_user_token_headers["Authorization"].split(" ")[1]
    with client.websocket_connect(f"/ws/channels/{test_channel['id']}?token={token}") as websocket:
        assert True

def test_ws_unauthorized_connection_missing_token(client: TestClient, test_channel):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/ws/channels/{test_channel['id']}?token="):
            pass
    assert exc_info.value.code == 1008

def test_ws_forbidden_channel_connection(client: TestClient, db, normal_user_token_headers, owner_token_headers, setup_ngo):
    import uuid
    # Create an invite_only group
    group_slug = f"test-group-{str(uuid.uuid4())[:8]}"
    group_res = client.post(
        f"/ngos/{setup_ngo['id']}/groups",
        headers=owner_token_headers,
        json={"name": "Secret Group", "slug": group_slug, "visibility": "invite_only"}
    )
    group = group_res.json()

    # Create an invite_only channel
    channel_res = client.post(
        f"/groups/{group['id']}/channels",
        headers=owner_token_headers,
        json={"name": "secret-channel", "visibility": "invite_only"}
    )
    invite_only_channel = channel_res.json()

    # The normal user is NOT a member of the group, so they should be forbidden
    token = normal_user_token_headers["Authorization"].split(" ")[1]
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/ws/channels/{invite_only_channel['id']}?token={token}") as websocket:
            pass
    assert exc_info.value.code == 1008

def test_ws_message_broadcast(client: TestClient, db, normal_user_token_headers, test_channel):
    token = normal_user_token_headers["Authorization"].split(" ")[1]

    with client.websocket_connect(f"/ws/channels/{test_channel['id']}?token={token}") as websocket:
        # Create a message via REST
        msg_data = {"content": "Test broadcast message", "type": "text"}
        response = client.post(
            f"/channels/{test_channel['id']}/messages",
            json=msg_data,
            headers=normal_user_token_headers
        )
        assert response.status_code == 201

        # We need to wait for the background task to run. In TestClient, background tasks run after the response is returned.
        data = websocket.receive_json()
        assert data["content"] == "Test broadcast message"
        assert data["channel_id"] == test_channel['id']

def test_ws_channel_isolation(client: TestClient, db, normal_user_token_headers, owner_token_headers, test_channel):
    token = normal_user_token_headers["Authorization"].split(" ")[1]

    # Create a second channel in the same group as test_channel
    ch_data = {"name": "isolated-channel", "visibility": "public"}
    response = client.post(
        f"/groups/{test_channel['group_id']}/channels",
        json=ch_data,
        headers=owner_token_headers
    )
    assert response.status_code == 201
    channel2_id = response.json()["id"]

    # Connect to channel 2
    with client.websocket_connect(f"/ws/channels/{channel2_id}?token={token}") as websocket:
        # Send a message to channel 1
        msg_data = {"content": "Message for channel 1", "type": "text"}
        response = client.post(
            f"/channels/{test_channel['id']}/messages",
            json=msg_data,
            headers=normal_user_token_headers
        )
        assert response.status_code == 201

        # websocket is connected to channel 2, it should NOT receive the message sent to channel 1
        # Send a message to channel 2 to ensure it ONLY gets the channel 2 message.

        msg_data2 = {"content": "Message for channel 2", "type": "text"}
        response2 = client.post(
            f"/channels/{channel2_id}/messages",
            json=msg_data2,
            headers=normal_user_token_headers
        )
        assert response2.status_code == 201

        data = websocket.receive_json()
        assert data["content"] == "Message for channel 2"
        assert data["channel_id"] == channel2_id
