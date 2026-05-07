import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User

def test_register_success(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepassword", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

def test_register_duplicate_email(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "anotherpassword"}
    )
    assert response.status_code == 400

def test_login_success(client: TestClient):
    # Register first
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "securepassword"}
    )

    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_credentials(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "wrong@example.com", "password": "securepassword"}
    )
    assert response.status_code == 400

def test_access_protected_route_with_token(client: TestClient):
    # Register and login
    client.post(
        "/auth/register",
        json={"email": "protected@example.com", "password": "securepassword"}
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "protected@example.com", "password": "securepassword"}
    )
    tokens = login_response.json()
    access_token = tokens["access_token"]

    # Access protected route
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "protected@example.com"

def test_access_protected_route_without_token(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_refresh_token_flow(client: TestClient):
    # Register and login
    client.post(
        "/auth/register",
        json={"email": "refresh@example.com", "password": "securepassword"}
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "refresh@example.com", "password": "securepassword"}
    )
    tokens = login_response.json()
    refresh_token = tokens["refresh_token"]

    # sleep for 1 second to ensure that the token is different due to exp change
    time.sleep(1)
    # Refresh token
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] != tokens["access_token"]  # Should be a new token

def test_invalid_refresh_token(client: TestClient):
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid_token_string"}
    )
    assert response.status_code == 401
