from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CookingSessionBase(BaseModel):
    recipe_id: Optional[int] = None


class CookingSessionCreate(CookingSessionBase):
    pass


class CookingSessionEnd(BaseModel):
    """Schema for ending a cooking session"""
    pass


class CookingSessionOut(CookingSessionBase):
    id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CookingSessionStats(BaseModel):
    """Statistics about user's cooking sessions"""
    total_sessions: int
    completed_sessions: int
    active_sessions: int
    total_cooking_minutes: int
    average_session_minutes: float
    most_cooked_recipe_id: Optional[int] = None
    most_cooked_recipe_title: Optional[str] = None
