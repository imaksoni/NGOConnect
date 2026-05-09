import io
from app.core.config import settings

def test_local_upload_attachment_success(client, normal_user_token, test_channel):
    # Ensure config uses local
    settings.STORAGE_BACKEND = "local"
    settings.LOCAL_STORAGE_DIR = "test_uploads"

    file_content = b"test file content"
    file_like = io.BytesIO(file_content)

    response = client.post(
        f"/channels/{test_channel['id']}/attachments/upload",
        headers={"Authorization": f"Bearer {normal_user_token}"},
        files={"file": ("test.txt", file_like, "text/plain")},
        data={"content": "Here is a file"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Here is a file"
    assert data["type"] == "file"
    assert len(data["attachments"]) == 1

    attachment = data["attachments"][0]
    assert attachment["file_name"] == "test.txt"
    assert attachment["content_type"] == "text/plain"

def test_upload_attachment_unauthorized(client, test_channel):
    file_content = b"test file content"
    file_like = io.BytesIO(file_content)

    response = client.post(
        f"/channels/{test_channel['id']}/attachments/upload",
        files={"file": ("test.txt", file_like, "text/plain")},
    )

    assert response.status_code == 401

def test_download_attachment_local(client, normal_user_token, test_channel):
    settings.STORAGE_BACKEND = "local"
    settings.LOCAL_STORAGE_DIR = "test_uploads"

    file_content = b"download test content"
    file_like = io.BytesIO(file_content)

    upload_res = client.post(
        f"/channels/{test_channel['id']}/attachments/upload",
        headers={"Authorization": f"Bearer {normal_user_token}"},
        files={"file": ("download.txt", file_like, "text/plain")}
    )

    assert upload_res.status_code == 201
    attachment_id = upload_res.json()["attachments"][0]["id"]

    download_res = client.get(
        f"/attachments/{attachment_id}/download",
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert download_res.status_code == 200
    assert download_res.content == file_content
