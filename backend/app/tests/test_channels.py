import pytest
from fastapi.testclient import TestClient

def test_create_channel(client: TestClient, db, owner_token_headers, setup_ngo):
    ngo_id = setup_ngo["id"]
    # Create group
    group_res = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Test Group for Channel", "slug": "test-group-channel"}
    )
    assert group_res.status_code == 201
    group_id = group_res.json()["id"]

    # Create channel
    channel_res = client.post(
        f"/groups/{group_id}/channels",
        headers=owner_token_headers,
        json={"name": "General Chat", "type": "chat", "visibility": "public"}
    )
    assert channel_res.status_code == 201
    channel = channel_res.json()
    assert channel["name"] == "General Chat"
    assert channel["type"] == "chat"
    assert channel["group_id"] == group_id

def test_max_channels_per_group(client: TestClient, db, owner_token_headers, setup_ngo):
    ngo_id = setup_ngo["id"]
    # Create group
    group_res = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Max Channels Group", "slug": "max-channels-group"}
    )
    assert group_res.status_code == 201
    group_id = group_res.json()["id"]

    # Create 5 channels
    for i in range(5):
        res = client.post(
            f"/groups/{group_id}/channels",
            headers=owner_token_headers,
            json={"name": f"Channel {i}", "type": "general", "visibility": "public"}
        )
        assert res.status_code == 201

    # Attempt to create 6th channel
    res6 = client.post(
        f"/groups/{group_id}/channels",
        headers=owner_token_headers,
        json={"name": "Channel 6", "type": "general", "visibility": "public"}
    )
    assert res6.status_code == 400
    assert "maximum of 5 channels" in res6.json()["detail"]

def test_get_channels(client: TestClient, db, owner_token_headers, setup_ngo):
    ngo_id = setup_ngo["id"]
    group_res = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "List Group", "slug": "list-group"}
    )
    group_id = group_res.json()["id"]

    client.post(
        f"/groups/{group_id}/channels",
        headers=owner_token_headers,
        json={"name": "Ch 1", "visibility": "public"}
    )
    client.post(
        f"/groups/{group_id}/channels",
        headers=owner_token_headers,
        json={"name": "Ch 2", "visibility": "invite_only"}
    )

    # Get channels list
    list_res = client.get(
        f"/groups/{group_id}/channels",
        headers=owner_token_headers
    )
    assert list_res.status_code == 200
    channels = list_res.json()
    assert len(channels) == 2

def test_get_single_channel(client: TestClient, db, owner_token_headers, setup_ngo):
    ngo_id = setup_ngo["id"]
    group_res = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Single Ch Group", "slug": "single-ch-group"}
    )
    group_id = group_res.json()["id"]

    ch_res = client.post(
        f"/groups/{group_id}/channels",
        headers=owner_token_headers,
        json={"name": "My Channel"}
    )
    ch_id = ch_res.json()["id"]

    get_res = client.get(
        f"/channels/{ch_id}",
        headers=owner_token_headers
    )
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "My Channel"

def test_update_channel(client: TestClient, db, owner_token_headers, setup_ngo):
    ngo_id = setup_ngo["id"]
    group_res = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Update Ch Group", "slug": "update-ch-group"}
    )
    group_id = group_res.json()["id"]

    ch_res = client.post(
        f"/groups/{group_id}/channels",
        headers=owner_token_headers,
        json={"name": "Old Name"}
    )
    ch_id = ch_res.json()["id"]

    update_res = client.patch(
        f"/channels/{ch_id}",
        headers=owner_token_headers,
        json={"name": "New Name"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Name"

def test_delete_channel(client: TestClient, db, owner_token_headers, setup_ngo):
    ngo_id = setup_ngo["id"]
    group_res = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Delete Ch Group", "slug": "delete-ch-group"}
    )
    group_id = group_res.json()["id"]

    ch_res = client.post(
        f"/groups/{group_id}/channels",
        headers=owner_token_headers,
        json={"name": "To be deleted"}
    )
    ch_id = ch_res.json()["id"]

    del_res = client.delete(
        f"/channels/{ch_id}",
        headers=owner_token_headers
    )
    assert del_res.status_code == 204

    get_res = client.get(
        f"/channels/{ch_id}",
        headers=owner_token_headers
    )
    assert get_res.status_code == 404
