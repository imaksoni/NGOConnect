import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.device import DeviceRegistration
from app.core.config import settings
import firebase_admin
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    if settings.FIREBASE_CREDENTIALS_PATH:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized with credentials path.")
    elif settings.FIREBASE_CREDENTIALS_JSON:
        import json
        cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized with credentials JSON.")
    else:
        logger.warning("Firebase credentials not configured. Push notifications will be disabled.")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

class NotificationService:
    def _is_configured(self) -> bool:
        try:
            firebase_admin.get_app()
            return True
        except ValueError:
            return False

    def get_active_devices(self, db: Session, user_id: str) -> List[DeviceRegistration]:
        return db.query(DeviceRegistration).filter(
            DeviceRegistration.user_id == user_id,
            DeviceRegistration.is_active == True
        ).all()

    def send_push_notification(self, db: Session, user_id: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> None:
        if not self._is_configured():
            logger.debug(f"Push notification skipped (not configured): to {user_id} - {title}")
            return

        devices = self.get_active_devices(db, user_id)
        if not devices:
            return

        tokens = [device.device_token for device in devices]

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            response = messaging.send_multicast(message)

            # Handle invalid tokens
            if response.failure_count > 0:
                responses = response.responses
                failed_tokens = []
                for idx, resp in enumerate(responses):
                    if not resp.success:
                        # The order of responses corresponds to the order of tokens
                        failed_tokens.append(tokens[idx])

                if failed_tokens:
                    logger.info(f"Deactivating {len(failed_tokens)} invalid device tokens for user {user_id}")
                    db.query(DeviceRegistration).filter(
                        DeviceRegistration.device_token.in_(failed_tokens)
                    ).update({"is_active": False}, synchronize_session=False)
                    db.commit()

        except Exception as e:
            logger.error(f"Error sending push notification to user {user_id}: {e}")

notification_service = NotificationService()
