from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    applicant = "applicant"
    admin = "admin"
    reviewer = "reviewer"
    superadmin = "superadmin"


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: UserRole
