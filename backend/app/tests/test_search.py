import pytest
from app.models.ngo import NgoVisibility, NgoVerificationStatus
from app.models.group import GroupVisibility
from app.models.event import EventVisibility

def test_search_ngos_public_verified(client, db, normal_user, normal_user_token_headers):
    test_user = normal_user
    auth_headers = normal_user_token_headers
    # Setup: Create a verified public NGO and a private/unverified one
    from app.services.ngo import ngo_service
    from app.schemas.ngo import NgoCreate

    # Verified Public NGO
    ngo1_in = NgoCreate(name="Global Rescue", slug="global-rescue", about="Rescue things", visibility="public")
    ngo1 = ngo_service.create_ngo(db, ngo1_in)
    ngo1.verification_status = NgoVerificationStatus.verified
    db.commit()

    # Private NGO
    ngo2_in = NgoCreate(name="Secret Group", slug="secret-group", about="Secret things", visibility="private")
    ngo2 = ngo_service.create_ngo(db, ngo2_in)
    ngo2.verification_status = NgoVerificationStatus.verified
    db.commit()

    # Search query
    response = client.get("/search/ngos?q=Rescue", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "global-rescue"

    # Search for secret group shouldn't return anything
    response = client.get("/search/ngos?q=Secret", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_search_groups(client, db, normal_user, normal_user_token_headers):
    test_user = normal_user
    auth_headers = normal_user_token_headers
    from app.services.ngo import ngo_service
    from app.schemas.ngo import NgoCreate
    from app.services.group import group_service
    from app.schemas.group import GroupCreate

    ngo_in = NgoCreate(name="Group NGO", slug="group-ngo", visibility="public")
    ngo = ngo_service.create_ngo(db, ngo_in)
    ngo.verification_status = NgoVerificationStatus.verified
    db.commit()

    # Public Group
    group1_in = GroupCreate(name="Public Chat", slug="public-chat", visibility="public")
    group1 = group_service.create_group(db, obj_in=group1_in, ngo_id=ngo.id, user_id=test_user["id"])

    # Private Group
    group2_in = GroupCreate(name="Private Chat", slug="private-chat", visibility="invite_only")
    group2 = group_service.create_group(db, obj_in=group2_in, ngo_id=ngo.id, user_id=test_user["id"])

    # Search as another user who is NOT a member
    # But wait, `test_user` is the creator, so they MIGHT be added as a member automatically?
    # group_service.create_group usually assigns group_admin to creator.

    # We will search using test_user
    response = client.get("/search/groups?q=Chat", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # test_user created both, so they should see both

    # Test without auth (only public)
    response = client.get("/search/groups?q=Chat")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "public-chat"

def test_search_events(client, db, owner_user, owner_token_headers):
    test_user = owner_user
    auth_headers = owner_token_headers
    from app.services.ngo import ngo_service
    from app.schemas.ngo import NgoCreate
    from app.services.event import event_service
    from app.schemas.event import EventCreate
    from datetime import datetime, timedelta

    ngo_in = NgoCreate(name="Event NGO", slug="event-ngo", visibility="public")
    ngo = ngo_service.create_ngo(db, ngo_in)
    ngo.verification_status = NgoVerificationStatus.verified

    from app.services.ngo_member import ngo_member_service
    ngo_member_service.add_owner(db, test_user["id"], ngo.id)
    db.commit()

    start = datetime.utcnow() + timedelta(days=1)
    end = datetime.utcnow() + timedelta(days=2)

    # Public Event
    event1_in = EventCreate(title="Public Picnic", start_time=start, end_time=end, visibility="public")
    event_service.create_ngo_event(db, ngo.id, event1_in, test_user["id"])

    # Private Event
    event2_in = EventCreate(title="Secret Meeting", start_time=start, end_time=end, visibility="members_only")
    event_service.create_ngo_event(db, ngo.id, event2_in, test_user["id"])
    # Search without auth
    response = client.get("/search/events?q=Picnic")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/search/events?q=Secret")
    assert response.status_code == 200
    assert len(response.json()) == 0

    # Search with auth
    response = client.get("/search/events?q=Secret", headers=auth_headers)
    assert response.status_code == 200
