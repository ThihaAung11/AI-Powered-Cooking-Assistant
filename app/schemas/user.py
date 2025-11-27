from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    username: str
    name: str
    email: EmailStr
    profile_url: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None  # Optional, will default to a role if not provided


class UserOut(UserBase):
    id: int
    is_active: bool
    role_id: int
    is_admin: bool
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserProfile(UserOut):
    """Extended user profile with statistics"""
    total_recipes: int = 0
    total_saved_recipes: int = 0
    total_cooking_sessions: int = 0
    total_feedbacks: int = 0
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """Detailed user statistics"""
    total_recipes_created: int
    total_recipes_saved: int
    total_cooking_sessions: int
    completed_cooking_sessions: int
    total_cooking_minutes: int
    total_feedbacks_given: int
    average_rating_given: float
    recipes_received_feedbacks: int
    average_rating_received: float
