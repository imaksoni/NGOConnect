import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_group_success(client: TestClient, owner_token_headers: dict, setup_ngo: dict):
    ngo_id = setup_ngo["id"]
    response = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={
            "name": "Test Group",
            "slug": "test-group",
            "about": "A test group",
            "visibility": "public"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Group"
    assert data["slug"] == "test-group"
    assert data["ngo_id"] == ngo_id
    assert data["visibility"] == "public"

def test_create_group_unauthorized(client: TestClient, normal_user_token_headers: dict, setup_ngo: dict):
    ngo_id = setup_ngo["id"]
    response = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=normal_user_token_headers,
        json={
            "name": "Another Group",
            "slug": "another-group"
        }
    )
    assert response.status_code == 403

def test_assign_role_success(client: TestClient, owner_token_headers: dict, setup_ngo: dict, normal_user: dict):
    # 1. Create a group
    ngo_id = setup_ngo["id"]
    create_resp = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Role Test", "slug": "role-test"}
    )
    group_id = create_resp.json()["id"]

    # 2. Assign role
    assign_resp = client.post(
        f"/groups/{group_id}/roles/assign",
        headers=owner_token_headers,
        json={
            "user_id": normal_user["id"],
            "role_name": "group_moderator"
        }
    )
    assert assign_resp.status_code == 200
    data = assign_resp.json()
    assert data["user_id"] == normal_user["id"]
    assert data["role"]["name"] == "group_moderator"

def test_assign_role_unauthorized(client: TestClient, normal_user_token_headers: dict, owner_token_headers: dict, setup_ngo: dict, normal_user: dict):
    # 1. Create a group as owner
    ngo_id = setup_ngo["id"]
    create_resp = client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Unauth Role Test", "slug": "unauth-role-test"}
    )
    group_id = create_resp.json()["id"]

    # 2. Normal user tries to assign a role
    assign_resp = client.post(
        f"/groups/{group_id}/roles/assign",
        headers=normal_user_token_headers,
        json={
            "user_id": normal_user["id"],
            "role_name": "group_admin"
        }
    )
    assert assign_resp.status_code == 403

def test_list_groups_visibility(client: TestClient, owner_token_headers: dict, normal_user_token_headers: dict, setup_ngo: dict):
    ngo_id = setup_ngo["id"]

    # Owner creates 1 public and 1 invite_only group
    client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Public Group", "slug": "pub-group", "visibility": "public"}
    )
    client.post(
        f"/ngos/{ngo_id}/groups",
        headers=owner_token_headers,
        json={"name": "Private Group", "slug": "priv-group", "visibility": "invite_only"}
    )

    # Owner can see both
    owner_resp = client.get(f"/ngos/{ngo_id}/groups", headers=owner_token_headers)
    assert owner_resp.status_code == 200
    assert len(owner_resp.json()) >= 2

    # Normal user (not in NGO) can only see public
    normal_resp = client.get(f"/ngos/{ngo_id}/groups", headers=normal_user_token_headers)
    assert normal_resp.status_code == 200

def test_create_join_request_success(client: TestClient, db: Session, normal_user_token_headers: dict, setup_ngo: dict, owner_token_headers: dict):
    ngo = setup_ngo
    owner_headers = owner_token_headers

    group_data = {
        "name": "Join Request Group",
        "slug": "join-request-group",
        "visibility": "invite_only"
    }
    response = client.post(f"/ngos/{ngo['id']}/groups", json=group_data, headers=owner_headers)
    group_id = response.json()["id"]

    normal_user_headers = normal_user_token_headers
    response = client.post(f"/groups/{group_id}/join-request", headers=normal_user_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["group_id"] == group_id

def test_duplicate_join_request_blocked(client: TestClient, db: Session, normal_user_token_headers: dict, setup_ngo: dict, owner_token_headers: dict):
    ngo = setup_ngo
    owner_headers = owner_token_headers

    group_data = {
        "name": "Join Request Group 2",
        "slug": "join-request-group-2",
        "visibility": "invite_only"
    }
    response = client.post(f"/ngos/{ngo['id']}/groups", json=group_data, headers=owner_headers)
    group_id = response.json()["id"]

    normal_user_headers = normal_user_token_headers
    response = client.post(f"/groups/{group_id}/join-request", headers=normal_user_headers)
    assert response.status_code == 201

    # Duplicate request
    response = client.post(f"/groups/{group_id}/join-request", headers=normal_user_headers)
    assert response.status_code == 400

def test_approve_join_request_success(client: TestClient, db: Session, normal_user_token_headers: dict, setup_ngo: dict, owner_token_headers: dict):
    ngo = setup_ngo
    owner_headers = owner_token_headers

    group_data = {
        "name": "Approve Group",
        "slug": "approve-group",
        "visibility": "invite_only"
    }
    response = client.post(f"/ngos/{ngo['id']}/groups", json=group_data, headers=owner_headers)
    group_id = response.json()["id"]

    normal_user_headers = normal_user_token_headers
    response = client.post(f"/groups/{group_id}/join-request", headers=normal_user_headers)
    assert response.status_code == 201
    request_id = response.json()["id"]

    # Approve request as admin
    response = client.post(f"/join-requests/{request_id}/approve", json={"admin_comment": "Welcome"}, headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["admin_comment"] == "Welcome"

    # Verify user is now a member
    response = client.get(f"/groups/{group_id}/members", headers=owner_headers)
    members = response.json()
    assert any(m["user_id"] == data["user_id"] for m in members)

def test_reject_join_request_success(client: TestClient, db: Session, normal_user_token_headers: dict, setup_ngo: dict, owner_token_headers: dict):
    ngo = setup_ngo
    owner_headers = owner_token_headers

    group_data = {
        "name": "Reject Group",
        "slug": "reject-group",
        "visibility": "invite_only"
    }
    response = client.post(f"/ngos/{ngo['id']}/groups", json=group_data, headers=owner_headers)
    group_id = response.json()["id"]

    normal_user_headers = normal_user_token_headers
    response = client.post(f"/groups/{group_id}/join-request", headers=normal_user_headers)
    assert response.status_code == 201
    request_id = response.json()["id"]

    # Reject request as admin
    response = client.post(f"/join-requests/{request_id}/reject", json={"admin_comment": "No"}, headers=owner_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

def test_unauthorized_approval_blocked(client: TestClient, db: Session, normal_user_token_headers: dict, setup_ngo: dict, owner_token_headers: dict, normal_user: dict):
    ngo = setup_ngo
    owner_headers = owner_token_headers

    group_data = {
        "name": "Unauth Group",
        "slug": "unauth-group",
        "visibility": "invite_only"
    }
    response = client.post(f"/ngos/{ngo['id']}/groups", json=group_data, headers=owner_headers)
    group_id = response.json()["id"]

    normal_user_headers = normal_user_token_headers
    response = client.post(f"/groups/{group_id}/join-request", headers=normal_user_headers)
    assert response.status_code == 201
    request_id = response.json()["id"]

    # Attempt to approve with unauthorized user
    user_2_headers = normal_user_token_headers # Same normal user
    response = client.post(f"/join-requests/{request_id}/approve", json={"admin_comment": "hi"}, headers=user_2_headers)
    assert response.status_code == 403
