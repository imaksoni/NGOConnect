from abc import ABC, abstractmethod
from typing import BinaryIO

class StorageProvider(ABC):
    @abstractmethod
    def upload_file(self, file_obj: BinaryIO, file_name: str, content_type: str) -> str:
        """
        Upload a file and return its storage key/path.
        """
        pass

    @abstractmethod
    def get_download_url(self, storage_key: str, file_name: str) -> str:
        """
        Get a presigned URL or a relative path for downloading the file.
        """
        pass

    @abstractmethod
    def get_file_path(self, storage_key: str) -> str | None:
        """
        Get the local file path if applicable (for local storage). Returns None for remote storage.
        """
        pass
