from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CollectionItemBase(BaseModel):
    recipe_id: int
    order: int = 0
    day_of_week: Optional[str] = None
    meal_type: Optional[str] = None
    notes: Optional[str] = None
    servings: Optional[int] = None


class CollectionItemCreate(CollectionItemBase):
    pass


class CollectionItemUpdate(BaseModel):
    order: Optional[int] = None
    day_of_week: Optional[str] = None
    meal_type: Optional[str] = None
    notes: Optional[str] = None
    servings: Optional[int] = None


class CollectionItemOut(CollectionItemBase):
    id: int
    collection_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecipeCollectionBase(BaseModel):
    name: str
    description: Optional[str] = None
    collection_type: str = "custom"  # "meal_plan", "favorites", "custom"
    is_public: bool = False


class RecipeCollectionCreate(RecipeCollectionBase):
    pass


class RecipeCollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    collection_type: Optional[str] = None
    is_public: Optional[bool] = None


class RecipeCollectionOut(RecipeCollectionBase):
    id: int
    user_id: int
    items: List[CollectionItemOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddRecipesToCollectionRequest(BaseModel):
    """Request to add multiple recipes to a collection"""
    recipe_ids: List[int]
    day_of_week: Optional[str] = None
    meal_type: Optional[str] = None
