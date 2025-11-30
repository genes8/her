"""Authentication endpoints - JWT + Google OAuth 2.0."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)
from app.core.exceptions import UnauthorizedError

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ============================================
# SCHEMAS
# ============================================


class UserCreate(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request schema."""

    refresh_token: str


class GoogleAuthRequest(BaseModel):
    """Google OAuth authorization code request."""

    code: str
    redirect_uri: str | None = None


class UserResponse(BaseModel):
    """User response schema."""

    id: str
    email: str
    full_name: str
    role: str
    is_active: bool


# ============================================
# TEMPORARY IN-MEMORY USER STORE
# ============================================
# TODO: Replace with database queries

_temp_users: dict[str, dict] = {}


def get_user_by_email(email: str) -> dict | None:
    """Get user by email from temporary store."""
    return _temp_users.get(email)


def create_user(email: str, password: str, full_name: str) -> dict:
    """Create user in temporary store."""
    user = {
        "id": str(len(_temp_users) + 1),
        "email": email,
        "password_hash": get_password_hash(password),
        "full_name": full_name,
        "role": "PLANNER",
        "is_active": True,
    }
    _temp_users[email] = user
    return user


# ============================================
# ENDPOINTS
# ============================================


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> UserResponse:
    """Register a new user with email and password."""
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    user = create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=user["is_active"],
    )


@router.post("/login", response_model=TokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
    """Login with email and password, returns JWT tokens."""
    user = get_user_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    access_token = create_access_token(
        subject=user["id"],
        additional_claims={"email": user["email"], "role": user["role"]},
    )
    refresh_token = create_refresh_token(subject=user["id"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        payload = verify_refresh_token(token_data.refresh_token)
        user_id = payload.get("sub")

        # TODO: Verify user still exists and is active in database

        access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )
    except UnauthorizedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/google", response_model=TokenResponse)
async def google_auth(auth_data: GoogleAuthRequest) -> TokenResponse:
    """
    Authenticate with Google OAuth 2.0.

    Exchange authorization code for tokens and create/update user.
    """
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    # TODO: Implement Google OAuth flow
    # 1. Exchange code for Google tokens
    # 2. Fetch user info from Google
    # 3. Create or update user in database
    # 4. Return JWT tokens

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth implementation pending",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserResponse:
    """Get current authenticated user."""
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")

        # TODO: Fetch user from database
        user = None
        for u in _temp_users.values():
            if u["id"] == user_id:
                user = u
                break

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            is_active=user["is_active"],
        )
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Logout user.

    Note: JWT tokens are stateless. For true logout, implement token blacklisting
    using Redis or database.
    """
    # TODO: Add token to blacklist in Redis
    return {"message": "Successfully logged out"}
