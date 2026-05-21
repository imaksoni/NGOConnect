import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.ngo import Ngo, NgoVisibility, NgoVerificationStatus
from app.models.user import User

def test_create_ngo(client: TestClient, db: Session, normal_user_token_headers: dict):
    response = client.post(
        "/ngos",
        json={"name": "Green Earth", "slug": "green-earth", "about": "Saving the planet", "visibility": "public"},
        headers=normal_user_token_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Green Earth"
    assert data["slug"] == "green-earth"
    assert data["visibility"] == "public"
    assert data["verification_status"] == "pending"
    assert "id" in data
    assert "invite_code" in data

def test_create_ngo_duplicate_slug(client: TestClient, db: Session, normal_user_token_headers: dict):
    # First NGO
    client.post(
        "/ngos",
        json={"name": "First NGO", "slug": "first-ngo"},
        headers=normal_user_token_headers,
    )
    # Second NGO with same slug
    response = client.post(
        "/ngos",
        json={"name": "Second NGO", "slug": "first-ngo"},
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "NGO with this slug already exists."

def test_discover_returns_only_public_verified(client: TestClient, db: Session, normal_user_token_headers: dict):
    # Create 3 NGOs with different statuses directly in DB
    from app.services.ngo import ngo_service
    from app.schemas.ngo import NgoCreate

    ngo1 = ngo_service.create_ngo(db, NgoCreate(name="NGO 1", slug="ngo-1", visibility="public"), creator_user_id="test-user")
    ngo2 = ngo_service.create_ngo(db, NgoCreate(name="NGO 2", slug="ngo-2", visibility="private"), creator_user_id="test-user")
    ngo3 = ngo_service.create_ngo(db, NgoCreate(name="NGO 3", slug="ngo-3", visibility="public"), creator_user_id="test-user")

    # Set verification statuses
    ngo1.verification_status = NgoVerificationStatus.verified
    ngo2.verification_status = NgoVerificationStatus.verified
    ngo3.verification_status = NgoVerificationStatus.pending
    db.commit()

    response = client.get("/ngos/discover")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "NGO 1"
    assert data[0]["visibility"] == "public"
    assert data[0]["verification_status"] == "verified"

def test_get_ngo_by_slug(client: TestClient, db: Session, normal_user_token_headers: dict):
    from app.services.ngo import ngo_service
    from app.schemas.ngo import NgoCreate

    ngo = ngo_service.create_ngo(db, NgoCreate(name="Find Me", slug="find-me", visibility="public"), creator_user_id="test-user")

    response = client.get(f"/ngos/slug/find-me")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Find Me"

    response_not_found = client.get("/ngos/slug/not-found")
    assert response_not_found.status_code == 404

def test_submit_verification_request(client: TestClient, db: Session, normal_user_token_headers: dict):
    # Create NGO first
    create_response = client.post(
        "/ngos",
        json={"name": "Verify Me", "slug": "verify-me"},
        headers=normal_user_token_headers,
    )
    ngo_id = create_response.json()["id"]

    # In DB simulation: update to 'rejected' to test transition to 'pending'
    ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
    ngo.verification_status = NgoVerificationStatus.rejected
    db.commit()

    response = client.post(
        f"/ngos/{ngo_id}/verify",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verification_status"] == "pending"
