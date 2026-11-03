from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResumeUpdateRequest(BaseModel):
    resume: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    resume: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SkillsUpdateRequest(BaseModel):
    skills: list[str]

class UserSkillsResponse(BaseModel):
    skills: list[str]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    message: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenVerify(BaseModel):
    access_token: str