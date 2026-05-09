import pytest
from datetime import datetime, timedelta
from app.models.ngo import NgoVerificationStatus
from app.models.ngo import Ngo

def test_create_public_event_verified_ngo(client, db, setup_ngo, owner_token_headers):
    # Setup test_ngo to be verified
    ngo_id = setup_ngo["id"]
    test_ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
    test_ngo.verification_status = NgoVerificationStatus.verified
    db.commit()

    payload = {
        "title": "Public Event",
        "description": "Anyone can join",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "visibility": "public"
    }

    response = client.post(f"/ngos/{ngo_id}/events", json=payload, headers=owner_token_headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Public Event"

def test_create_public_event_non_verified_ngo(client, db, setup_ngo, owner_token_headers):
    ngo_id = setup_ngo["id"]
    test_ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
    test_ngo.verification_status = NgoVerificationStatus.pending
    db.commit()

    payload = {
        "title": "Invalid Public Event",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "visibility": "public"
    }

    response = client.post(f"/ngos/{ngo_id}/events", json=payload, headers=owner_token_headers)
    assert response.status_code == 403
    assert "Non-verified NGOs cannot publish public events" in response.json()["detail"]

def test_create_members_only_event_non_verified_ngo(client, db, setup_ngo, owner_token_headers):
    ngo_id = setup_ngo["id"]
    test_ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
    test_ngo.verification_status = NgoVerificationStatus.pending
    db.commit()

    payload = {
        "title": "Members Only Event",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "visibility": "members_only"
    }

    response = client.post(f"/ngos/{ngo_id}/events", json=payload, headers=owner_token_headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Members Only Event"
    assert response.json()["visibility"] == "members_only"
