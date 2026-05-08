import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def create_group_and_channel(client, ngo, owner_token_headers):
    import uuid
    # create group
    slug = f"cg-{uuid.uuid4().hex[:6]}"
    res_group = client.post(
        f"/ngos/{ngo['id']}/groups",
        headers=owner_token_headers,
        json={"name": "Chat Group", "slug": slug, "visibility": "public"}
    )
    group = res_group.json()

    # create channel
    c_slug = f"ch-{uuid.uuid4().hex[:6]}"
    res_channel = client.post(
        f"/groups/{group['id']}/channels",
        headers=owner_token_headers,
        json={"name": "general", "slug": c_slug, "type": "chat", "visibility": "public"}
    )
    channel = res_channel.json()
    return group, channel

def test_send_message_success(client: TestClient, db: Session, owner_token_headers, setup_ngo):
    group, channel = create_group_and_channel(client, setup_ngo, owner_token_headers)

    response = client.post(
        f"/channels/{channel['id']}/messages",
        headers=owner_token_headers,
        json={"content": "Hello World", "type": "text"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Hello World"
    assert "id" in data

def test_list_messages_success(client: TestClient, db: Session, owner_token_headers, setup_ngo):
    group, channel = create_group_and_channel(client, setup_ngo, owner_token_headers)

    # Send a message
    client.post(
        f"/channels/{channel['id']}/messages",
        headers=owner_token_headers,
        json={"content": "First Message", "type": "text"}
    )

    # List messages
    response = client.get(
        f"/channels/{channel['id']}/messages",
        headers=owner_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["content"] == "First Message"

def test_unauthorized_read_blocked(client: TestClient, db: Session, owner_token_headers, normal_user_token_headers, setup_ngo):
    import uuid
    # Create an invite_only group (normal user is not a member)
    res_group = client.post(
        f"/ngos/{setup_ngo['id']}/groups",
        headers=owner_token_headers,
        json={"name": "Secret Group", "slug": f"sec-{uuid.uuid4().hex[:6]}", "visibility": "invite_only"}
    )
    group = res_group.json()

    res_channel = client.post(
        f"/groups/{group['id']}/channels",
        headers=owner_token_headers,
        json={"name": "secret-chat", "slug": f"sc-{uuid.uuid4().hex[:6]}", "visibility": "public"} # visibility of channel doesn't matter if group is invite_only and user not in it
    )
    channel = res_channel.json()

    response = client.get(
        f"/channels/{channel['id']}/messages",
        headers=normal_user_token_headers
    )
    assert response.status_code == 403

def test_unauthorized_write_blocked(client: TestClient, db: Session, owner_token_headers, normal_user_token_headers, setup_ngo):
    import uuid
    # Create an invite_only group (normal user is not a member)
    res_group = client.post(
        f"/ngos/{setup_ngo['id']}/groups",
        headers=owner_token_headers,
        json={"name": "Secret Group", "slug": f"sec2-{uuid.uuid4().hex[:6]}", "visibility": "invite_only"}
    )
    group = res_group.json()

    res_channel = client.post(
        f"/groups/{group['id']}/channels",
        headers=owner_token_headers,
        json={"name": "secret-chat", "slug": f"sc2-{uuid.uuid4().hex[:6]}", "visibility": "public"}
    )
    channel = res_channel.json()

    response = client.post(
        f"/channels/{channel['id']}/messages",
        headers=normal_user_token_headers,
        json={"content": "Hack", "type": "text"}
    )
    assert response.status_code == 403

def test_attachment_metadata_creation_success(client: TestClient, db: Session, owner_token_headers, setup_ngo):
    group, channel = create_group_and_channel(client, setup_ngo, owner_token_headers)

    # Send a message
    msg_response = client.post(
        f"/channels/{channel['id']}/messages",
        headers=owner_token_headers,
        json={"content": "Here is a file", "type": "text"}
    )
    msg_id = msg_response.json()["id"]

    # Create attachment
    att_response = client.post(
        f"/messages/{msg_id}/attachments",
        headers=owner_token_headers,
        json={
            "file_name": "report.pdf",
            "content_type": "application/pdf",
            "file_size": 1024,
            "storage_key": "s3://bucket/report.pdf"
        }
    )
    assert att_response.status_code == 201
    att_data = att_response.json()
    assert att_data["file_name"] == "report.pdf"
    assert att_data["storage_key"] == "s3://bucket/report.pdf"
