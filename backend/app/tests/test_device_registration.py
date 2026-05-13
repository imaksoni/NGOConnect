import pytest
from app.models.device import DeviceRegistration

def test_device_registration_success(client, normal_user_token_headers, db):
    response = client.post(
        "/devices/register",
        headers=normal_user_token_headers,
        json={
            "device_token": "test-token-123",
            "platform": "ios"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["device_token"] == "test-token-123"
    assert data["platform"] == "ios"
    assert data["is_active"] == True
    assert "id" in data

    # Verify db
    db_device = db.query(DeviceRegistration).filter_by(device_token="test-token-123").first()
    assert db_device is not None
    assert db_device.platform == "ios"

def test_device_registration_duplicate_handling(client, normal_user_token_headers, owner_token_headers, normal_user, owner_user, db):
    # User 1 registers token
    client.post(
        "/devices/register",
        headers=normal_user_token_headers,
        json={"device_token": "shared-token", "platform": "android"}
    )

    db_device1 = db.query(DeviceRegistration).filter_by(device_token="shared-token").first()
    assert db_device1.user_id == normal_user["id"]

    # User 2 logs in on same device, registers same token
    response = client.post(
        "/devices/register",
        headers=owner_token_headers,
        json={"device_token": "shared-token", "platform": "android"}
    )
    assert response.status_code == 200

    # Verify db ownership changed
    db_device2 = db.query(DeviceRegistration).filter_by(device_token="shared-token").first()
    assert db_device2.user_id == owner_user["id"]
    # Verify count remains 1
    assert db.query(DeviceRegistration).filter_by(device_token="shared-token").count() == 1

def test_device_registration_unauthorized(client):
    response = client.post(
        "/devices/register",
        json={"device_token": "test-token-123", "platform": "ios"}
    )
    assert response.status_code == 401

def test_device_unregister(client, normal_user_token_headers, db):
    client.post(
        "/devices/register",
        headers=normal_user_token_headers,
        json={"device_token": "test-token-123", "platform": "ios"}
    )

    response = client.post(
        "/devices/unregister",
        headers=normal_user_token_headers,
        json={"device_token": "test-token-123"}
    )
    assert response.status_code == 200

    db_device = db.query(DeviceRegistration).filter_by(device_token="test-token-123").first()
    assert db_device.is_active == False
