from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
import uuid

from auth.models import UserRegisterRequest, UserLoginRequest, TokenRefreshRequest, TokenResponse
from auth.utils import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_refresh_token
)
from auth.middleware import get_current_user
from db_config import DatabaseConfig

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_to_dict(user: dict) -> dict:
    return {
        "user_id": user["_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    db = await DatabaseConfig.get_database()

    existing = await db.users.find_one({"email": request.email.lower()})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user_id = str(uuid.uuid4())
    user_doc = {
        "_id": user_id,
        "name": request.name,
        "email": request.email.lower(),
        "hashed_password": hash_password(request.password),
        "role": "applicant",
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }
    await db.users.insert_one(user_doc)

    token_data = {"sub": user_id, "role": "applicant"}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=_user_to_dict(user_doc),
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    db = await DatabaseConfig.get_database()

    user = await db.users.find_one({"email": request.email.lower()})
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    token_data = {"sub": user["_id"], "role": user["role"]}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=_user_to_dict(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefreshRequest):
    payload = decode_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    db = await DatabaseConfig.get_database()
    user = await db.users.find_one({"_id": payload.get("sub")})
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    token_data = {"sub": user["_id"], "role": user["role"]}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=_user_to_dict(user),
    )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return _user_to_dict(current_user)


@router.post("/logout")
async def logout():
    # Stateless JWT — client deletes tokens. Redis blacklist can be added here later.
    return {"message": "Logged out successfully"}
