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

from unittest.mock import patch
from fastapi import HTTPException

def test_google_login_success_new_user(client: TestClient):
    with patch("app.api.routers.auth.verify_google_token") as mock_verify:
        mock_verify.return_value = {
            "email": "newgoogleuser@example.com",
            "sub": "google_123456",
            "name": "Google User"
        }

        response = client.post(
            "/auth/google",
            json={"id_token": "fake_google_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        mock_verify.assert_called_once_with("fake_google_token")

def test_google_login_success_existing_user(client: TestClient):
    # First create the user
    client.post(
        "/auth/register",
        json={"email": "existinggoogle@example.com", "password": "securepassword", "full_name": "Existing User"}
    )

    with patch("app.api.routers.auth.verify_google_token") as mock_verify:
        mock_verify.return_value = {
            "email": "existinggoogle@example.com",
            "sub": "google_654321",
            "name": "Existing Google User"
        }

        response = client.post(
            "/auth/google",
            json={"id_token": "fake_google_token_existing"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        mock_verify.assert_called_once_with("fake_google_token_existing")

def test_google_login_invalid_token(client: TestClient):
    with patch("app.api.routers.auth.verify_google_token") as mock_verify:
        mock_verify.side_effect = HTTPException(status_code=400, detail="Token used too early")

        response = client.post(
            "/auth/google",
            json={"id_token": "invalid_token"}
        )
        assert response.status_code == 400
        mock_verify.assert_called_once_with("invalid_token")
