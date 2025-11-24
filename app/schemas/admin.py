from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Management Schemas
class AdminUserOut(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr
    profile_url: Optional[str] = None
    is_active: bool
    role_id: int
    role_name: str
    created_at: datetime
    total_recipes: int = 0
    total_cooking_sessions: int = 0
    total_feedbacks: int = 0
    
    class Config:
        from_attributes = True


class AdminUserList(BaseModel):
    total: int
    users: List[AdminUserOut]


class UserDeactivate(BaseModel):
    reason: Optional[str] = None


# Recipe Management Schemas
class AdminRecipeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    total_time: Optional[int] = None
    ingredients: str
    is_public: bool = True


class AdminRecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    total_time: Optional[int] = None
    ingredients: Optional[str] = None
    is_public: Optional[bool] = None


class AdminRecipeOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    total_time: Optional[int] = None
    ingredients: str
    image_url: Optional[str] = None
    is_public: bool
    created_by: int
    creator_name: str
    created_at: datetime
    feedbacks_count: int = 0
    average_rating: float = 0.0
    
    class Config:
        from_attributes = True


# Comment/Feedback Management Schemas
class AdminFeedbackOut(BaseModel):
    id: int
    user_id: int
    username: str
    recipe_id: int
    recipe_title: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminFeedbackList(BaseModel):
    total: int
    feedbacks: List[AdminFeedbackOut]


class FeedbackRemoveReason(BaseModel):
    reason: str


# Cooking History Analytics Schemas
class CookingHistoryItem(BaseModel):
    session_id: int
    user_id: int
    username: str
    recipe_id: Optional[int] = None
    recipe_title: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    
    class Config:
        from_attributes = True


class CookingHistoryList(BaseModel):
    total: int
    sessions: List[CookingHistoryItem]


class CookingAnalytics(BaseModel):
    total_sessions: int
    completed_sessions: int
    total_cooking_time_minutes: int
    average_session_duration_minutes: float
    most_cooked_recipes: List[dict]  # [{recipe_id, recipe_title, count}]
    top_active_users: List[dict]  # [{user_id, username, session_count}]


# AI Knowledge Management Schemas
class AIKnowledgeRefreshResponse(BaseModel):
    success: bool
    message: str
    recipes_processed: int = 0
    embeddings_created: int = 0


class RecipeDataUpdate(BaseModel):
    recipe_ids: Optional[List[int]] = None  # If None, update all recipes
    force_refresh: bool = False
