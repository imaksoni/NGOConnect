from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import User, UserCreate, UserLogin
from app.schemas.token import Token
from app.repositories.user import user_repository
from app.repositories.auth_provider import auth_provider_repository
from app.schemas.auth_provider import AuthProviderCreate
from app.services.auth import auth_service
from app.services.google_auth import verify_google_token
from app.core.security import create_access_token, create_refresh_token, verify_token
from pydantic import BaseModel
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    user = user_repository.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = user_repository.create(db, user_in=user_in)
    from app.core.analytics import analytics_service
    analytics_service.log_event(
        event_name="user_registered",
        actor_user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        metadata={"method": "email"}
    )
    return user

from fastapi.security import OAuth2PasswordRequestForm

class GoogleAuthRequest(BaseModel):
    id_token: str

@router.post("/google", response_model=Token)
def login_with_google(
    request: GoogleAuthRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Login or register a user via Google Sign-In.
    """
    idinfo = verify_google_token(request.id_token)

    email = idinfo.get("email")
    google_user_id = idinfo.get("sub")
    name = idinfo.get("name")

    if not email or not google_user_id:
        raise HTTPException(status_code=400, detail="Invalid token payload from Google")

    user = user_repository.get_by_email(db, email=email)

    if not user:
        # Create user
        user_in = UserCreate(email=email, full_name=name)
        user = user_repository.create(db, user_in=user_in)
        from app.core.analytics import analytics_service
        analytics_service.log_event(
            event_name="user_registered",
            actor_user_id=user.id,
            entity_type="user",
            entity_id=user.id,
            metadata={"method": "google"}
        )

    # Link auth provider if not linked
    auth_provider = auth_provider_repository.get_by_provider_id(db, provider="google", provider_user_id=google_user_id)
    if not auth_provider:
        auth_provider_in = AuthProviderCreate(
            user_id=user.id,
            provider="google",
            provider_user_id=google_user_id
        )
        auth_provider_repository.create(db, auth_provider_in=auth_provider_in)

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Login a user and return access and refresh tokens.
    """
    user_in = UserLogin(email=form_data.username, password=form_data.password)
    user = auth_service.authenticate(db, user_in=user_in)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
) -> Any:
    """
    Refresh access token.
    """
    payload = verify_token(refresh_token, "refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    user = user_repository.get_by_id(db, user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.get("/me", response_model=User)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
