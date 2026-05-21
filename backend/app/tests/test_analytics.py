import logging
import json
from unittest.mock import patch
from app.core.analytics import AnalyticsService

def test_analytics_service_logs_json(caplog):
    service = AnalyticsService()

    with caplog.at_level(logging.INFO, logger="analytics"):
        service.log_event(
            event_name="test_event",
            actor_user_id="user_1",
            entity_type="test_entity",
            entity_id="entity_1",
            metadata={"source": "test"}
        )

    # Check that a log was emitted
    assert len(caplog.records) == 1
    record = caplog.records[0]

    # Verify basic message
    assert record.message == "Analytics Event: test_event"
    assert record.name == "analytics"

    # Verify the structured 'analytics_event' attribute was added
    assert hasattr(record, "analytics_event")
    event_data = record.analytics_event
    assert event_data["event_name"] == "test_event"
    assert event_data["actor_user_id"] == "user_1"
    assert event_data["entity_type"] == "test_entity"
    assert event_data["entity_id"] == "entity_1"
    assert event_data["metadata"] == {"source": "test"}
