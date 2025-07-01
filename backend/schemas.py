from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    username: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    provider: str
    provider_id: str
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserProfile(UserBase):
    id: int
    provider: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    friends: List['UserProfile'] = []

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    provider: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class OAuthUserInfo(BaseModel):
    email: str
    name: str
    picture: Optional[str] = None
    provider: str
    provider_id: str

# fix forward reference
UserProfile.model_rebuild()
