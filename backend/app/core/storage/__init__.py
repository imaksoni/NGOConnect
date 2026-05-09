from .base import StorageProvider
from .local import LocalStorageProvider
from .s3 import S3StorageProvider
from app.core.config import settings

def get_storage_provider() -> StorageProvider:
    if settings.STORAGE_BACKEND == "s3":
        return S3StorageProvider()
    return LocalStorageProvider()

storage_provider = get_storage_provider()
