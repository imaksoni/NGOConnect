from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.models.base import Base

class DeviceRegistration(Base):
    __tablename__ = "device_registrations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    device_token = Column(String, unique=True, index=True, nullable=False)
    platform = Column(String, nullable=False) # 'android', 'ios', 'web'
    app_version = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
