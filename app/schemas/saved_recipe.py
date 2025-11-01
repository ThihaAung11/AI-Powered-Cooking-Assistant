from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .recipe import RecipeOut


class SavedRecipeCreate(BaseModel):
    recipe_id: int


class SavedRecipeOut(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SavedRecipeWithDetails(SavedRecipeOut):
    """Saved recipe with full recipe details"""
    recipe: Optional[RecipeOut] = None

    class Config:
        from_attributes = True
