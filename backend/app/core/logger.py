import logging
import json
import uuid
import contextvars
from datetime import datetime, timezone

# Context variable to store request ID across the async/sync call stack
request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="system"
)

def get_request_id() -> str:
    return request_id_ctx_var.get()

SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token", "secret", "id_token", "authorization", "device_token", "fcm_token"}

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    Filters out sensitive keys from the extras/message.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _filter_sensitive_data(self, data: dict) -> dict:
        filtered = {}
        for k, v in data.items():
            if k.lower() in SENSITIVE_KEYS:
                filtered[k] = "***"
            elif isinstance(v, dict):
                filtered[k] = self._filter_sensitive_data(v)
            else:
                filtered[k] = v
        return filtered

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "request_id": get_request_id(),
        }

        # Add extra fields passed in logger.info(msg, extra={"key": "value"})
        if hasattr(record, "analytics_event"):
             log_data["analytics_event"] = record.analytics_event

        extra_data = {}
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord(None, None, "", 0, "", (), None, None).__dict__ and key != "message":
                extra_data[key] = value

        if extra_data:
            log_data["extra"] = self._filter_sensitive_data(extra_data)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging():
    logger = logging.getLogger()

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(logging.INFO)

    logHandler = logging.StreamHandler()
    logHandler.setFormatter(JsonFormatter())
    logger.addHandler(logHandler)

    # Make standard library loggers quieter or structured
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

setup_logging()
