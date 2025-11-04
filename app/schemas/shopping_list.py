from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ShoppingListItemBase(BaseModel):
    ingredient: str
    quantity: Optional[str] = None
    category: str = "Other"
    is_checked: bool = False
    notes: Optional[str] = None
    source_recipe_id: Optional[int] = None


class ShoppingListItemCreate(ShoppingListItemBase):
    pass


class ShoppingListItemUpdate(BaseModel):
    ingredient: Optional[str] = None
    quantity: Optional[str] = None
    category: Optional[str] = None
    is_checked: Optional[bool] = None
    notes: Optional[str] = None


class ShoppingListItemOut(ShoppingListItemBase):
    id: int
    shopping_list_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShoppingListBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_completed: bool = False


class ShoppingListCreate(ShoppingListBase):
    items: List[ShoppingListItemCreate] = []


class ShoppingListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None


class ShoppingListOut(ShoppingListBase):
    id: int
    user_id: int
    items: List[ShoppingListItemOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateShoppingListRequest(BaseModel):
    """Request to generate shopping list from recipes or collection"""
    recipe_ids: Optional[List[int]] = None
    collection_id: Optional[int] = None
    list_name: str = "Shopping List"
