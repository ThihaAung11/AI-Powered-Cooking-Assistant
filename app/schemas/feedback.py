from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000)


class FeedbackCreate(FeedbackBase):
    recipe_id: int


class FeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000)


class FeedbackOut(FeedbackBase):
    id: int
    user_id: int
    recipe_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackWithUser(FeedbackOut):
    """Feedback with user information"""
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
