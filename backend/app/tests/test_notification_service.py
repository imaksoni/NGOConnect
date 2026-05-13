import pytest
from app.services.notification import NotificationService
from app.models.device import DeviceRegistration
from app.models.user import User

class MockResponse:
    def __init__(self, failure_count, responses):
        self.failure_count = failure_count
        self.responses = responses

class MockResponseItem:
    def __init__(self, success):
        self.success = success

class MockMessaging:
    def __init__(self):
        self.sent_messages = []
        self.mock_response = MockResponse(0, [])

    def MulticastMessage(self, notification, data, tokens):
        return {"notification": notification, "data": data, "tokens": tokens}

    def send_multicast(self, message):
        self.sent_messages.append(message)
        return self.mock_response

    def Notification(self, title, body):
        return {"title": title, "body": body}

@pytest.fixture
def mock_messaging(monkeypatch):
    mock = MockMessaging()
    import app.services.notification
    monkeypatch.setattr(app.services.notification, "messaging", mock)
    return mock

def test_push_send_service_invocation(db, normal_user, mock_messaging, monkeypatch):
    service = NotificationService()
    monkeypatch.setattr(service, "_is_configured", lambda: True)

    # Register a device
    device = DeviceRegistration(
        id="dev1",
        user_id=normal_user["id"],
        device_token="valid-token",
        platform="ios",
        is_active=True
    )
    db.add(device)
    db.commit()

    service.send_push_notification(
        db,
        user_id=normal_user["id"],
        title="Test Title",
        body="Test Body",
        data={"key": "val"}
    )

    assert len(mock_messaging.sent_messages) == 1
    sent_msg = mock_messaging.sent_messages[0]
    assert "valid-token" in sent_msg["tokens"]
    assert sent_msg["notification"]["title"] == "Test Title"
    assert sent_msg["data"] == {"key": "val"}

def test_invalid_token_deactivation(db, normal_user, mock_messaging, monkeypatch):
    service = NotificationService()
    monkeypatch.setattr(service, "_is_configured", lambda: True)

    # Register two devices
    device1 = DeviceRegistration(
        id="dev1", user_id=normal_user["id"], device_token="valid-token", platform="ios", is_active=True
    )
    device2 = DeviceRegistration(
        id="dev2", user_id=normal_user["id"], device_token="invalid-token", platform="ios", is_active=True
    )
    db.add_all([device1, device2])
    db.commit()

    # Mock response: 1 failure, 1 success
    # Order matches tokens: ["valid-token", "invalid-token"]
    mock_messaging.mock_response = MockResponse(
        failure_count=1,
        responses=[MockResponseItem(True), MockResponseItem(False)]
    )

    service.send_push_notification(
        db,
        user_id=normal_user["id"],
        title="Test",
        body="Test"
    )

    # Check db
    db.refresh(device1)
    db.refresh(device2)

    assert device1.is_active == True
    assert device2.is_active == False
