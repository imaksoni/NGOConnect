import boto3
import uuid
import os
from typing import BinaryIO
from botocore.exceptions import ClientError
from .base import StorageProvider
from app.core.config import settings

class S3StorageProvider(StorageProvider):
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(self, file_obj: BinaryIO, file_name: str, content_type: str) -> str:
        ext = os.path.splitext(file_name)[1]
        unique_key = f"uploads/{uuid.uuid4()}{ext}"

        self.s3_client.upload_fileobj(
            file_obj,
            self.bucket_name,
            unique_key,
            ExtraArgs={"ContentType": content_type}
        )

        return unique_key

    def get_download_url(self, storage_key: str, file_name: str) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": storage_key,
                    "ResponseContentDisposition": f'attachment; filename="{file_name}"'
                },
                ExpiresIn=3600  # 1 hour
            )
            return url
        except ClientError as e:
            # Fallback or logging could be added here
            return ""

    def get_file_path(self, storage_key: str) -> str | None:
        return None
