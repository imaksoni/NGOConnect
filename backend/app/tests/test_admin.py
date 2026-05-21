from fastapi.testclient import TestClient
from app.models.user import User
from app.models.ngo import Ngo, NgoVerificationStatus
from app.models.audit_log import AuditLog

def test_admin_access_forbidden(client: TestClient, db, normal_user_token_headers):
    response = client.get("/admin/audit-logs", headers=normal_user_token_headers)
    assert response.status_code == 403

def test_admin_access_allowed_and_actions(client: TestClient, db, normal_user_token_headers, normal_user):
    user_token_headers = normal_user_token_headers

    # Make the user an admin
    user = db.query(User).filter(User.id == normal_user["id"]).first()
    user.is_platform_admin = True
    db.commit()

    # Create a pending NGO
    from app.services.ngo import ngo_service
    from app.schemas.ngo import NgoCreate
    ngo_in = NgoCreate(name="Test NGO", slug="test-ngo", visibility="public")
    ngo = ngo_service.create_ngo(db, ngo_in, creator_user_id=normal_user["id"])

    # Admin accesses verification requests
    response = client.get("/admin/moderation/verification-requests", headers=user_token_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == ngo.id

    # Admin verifies NGO
    response = client.post(f"/admin/ngos/{ngo.id}/verify", headers=user_token_headers)
    assert response.status_code == 200
    assert response.json()["verification_status"] == "verified"

    # Check audit log is created
    response = client.get("/admin/audit-logs", headers=user_token_headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) > 0
    assert logs[0]["action_type"] == "verify_ngo"
    assert logs[0]["entity_id"] == ngo.id
