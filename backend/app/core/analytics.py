import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("analytics")

class AnalyticsService:
    def log_event(
        self,
        event_name: str,
        actor_user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Logs a business analytics event as structured JSON metadata.
        """
        event_data = {
            "event_name": event_name,
            "actor_user_id": actor_user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
        }

        if metadata:
            event_data["metadata"] = metadata

        logger.info(
            f"Analytics Event: {event_name}",
            extra={
                "analytics_event": event_data
            }
        )

analytics_service = AnalyticsService()