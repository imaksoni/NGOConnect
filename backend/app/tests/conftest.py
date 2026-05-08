import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db
from app.models.base import Base

# Create a fresh in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    # We clear the tables before each test to have a clean state
    # A cleaner approach is transaction rollback but this works well for in-memory SQLite
    for table in reversed(Base.metadata.sorted_tables):
        with engine.begin() as conn:
            conn.execute(table.delete())

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture
def normal_user(client: TestClient, db):
    import uuid
    email = f"normal_{uuid.uuid4()}@example.com"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "password123", "full_name": "Normal User"}
    )
    return response.json()

@pytest.fixture
def normal_user_token_headers(client: TestClient, db, normal_user):
    login_response = client.post(
        "/auth/login",
        data={"username": normal_user["email"], "password": "password123"}
    )
    tokens = login_response.json()
    a_token = tokens["access_token"]
    return {"Authorization": f"Bearer {a_token}"}

@pytest.fixture
def owner_user(client: TestClient, db):
    import uuid
    email = f"owner_{uuid.uuid4()}@example.com"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "password123", "full_name": "Owner User"}
    )
    return response.json()

@pytest.fixture
def owner_token_headers(client: TestClient, db, owner_user):
    login_response = client.post(
        "/auth/login",
        data={"username": owner_user["email"], "password": "password123"}
    )
    tokens = login_response.json()
    a_token = tokens["access_token"]
    return {"Authorization": f"Bearer {a_token}"}

@pytest.fixture
def setup_ngo(client: TestClient, db, owner_token_headers):
    import uuid
    slug = f"test-ngo-{str(uuid.uuid4())[:8]}"
    response = client.post(
        "/ngos",
        headers=owner_token_headers,
        json={"name": "Test NGO", "slug": slug, "about": "Testing"}
    )
    return response.json()
