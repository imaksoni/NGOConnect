import os
import shutil
import uuid
from typing import BinaryIO
from .base import StorageProvider
from app.core.config import settings

class LocalStorageProvider(StorageProvider):
    def __init__(self):
        self.upload_dir = settings.LOCAL_STORAGE_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_file(self, file_obj: BinaryIO, file_name: str, content_type: str) -> str:
        # Generate a unique filename to prevent collisions
        ext = os.path.splitext(file_name)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(self.upload_dir, unique_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)

        return unique_name

    def get_download_url(self, storage_key: str, file_name: str) -> str:
        # For local, we will return a relative API path that our endpoint will handle
        return f"/attachments/{storage_key}/download"

    def get_file_path(self, storage_key: str) -> str | None:
        return os.path.join(self.upload_dir, storage_key)
