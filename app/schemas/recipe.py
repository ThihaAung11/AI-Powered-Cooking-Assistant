from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CookingStepBase(BaseModel):
    step_number: int
    instruction_text: str
    media_url: Optional[str] = None


class CookingStepCreate(CookingStepBase):
    pass


class CookingStepOut(CookingStepBase):
    id: int
    recipe_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    total_time: Optional[int] = None  # minutes
    ingredients: str
    image_url: Optional[str] = None
    is_public: bool = True


class RecipeCreate(RecipeBase):
    steps: List[CookingStepCreate] = []


class RecipeSearchFilter(BaseModel):
    """Search and filter parameters for recipes"""
    search: Optional[str] = None  # Search in title, description, ingredients
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    min_time: Optional[int] = None  # Minimum cooking time in minutes
    max_time: Optional[int] = None  # Maximum cooking time in minutes
    ingredients: Optional[str] = None  # Search for specific ingredients
    created_by: Optional[int] = None  # Filter by creator
    include_private: bool = False  # Include private recipes (only for owner)


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    total_time: Optional[int] = None
    ingredients: Optional[str] = None
    image_url: Optional[str] = None
    is_public: Optional[bool] = None
    steps: Optional[List[CookingStepCreate]] = None


class RecipeOut(RecipeBase):
    id: int
    created_by: int
    is_public: bool
    steps: List[CookingStepOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
