import json
import logging
from app.core.logger import JsonFormatter, get_request_id, request_id_ctx_var

def test_json_formatter_basic():
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None
    )
    formatter = JsonFormatter()
    output = formatter.format(record)
    data = json.loads(output)

    assert data["level"] == "INFO"
    assert data["message"] == "Test message"
    assert data["logger_name"] == "test_logger"
    assert "timestamp" in data
    assert "request_id" in data

def test_json_formatter_filters_sensitive_keys():
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None
    )
    # Add extra attributes
    record.password = "supersecret"
    record.token = "abc123token"
    record.user_id = "user123"
    record.fcm_token = "fcm_xyz"

    formatter = JsonFormatter()
    output = formatter.format(record)
    data = json.loads(output)

    assert data["extra"]["password"] == "***"
    assert data["extra"]["token"] == "***"
    assert data["extra"]["fcm_token"] == "***"
    assert data["extra"]["user_id"] == "user123"

def test_request_id_context_var():
    token = request_id_ctx_var.set("test-corr-id-123")
    assert get_request_id() == "test-corr-id-123"
    request_id_ctx_var.reset(token)
    assert get_request_id() == "system"
