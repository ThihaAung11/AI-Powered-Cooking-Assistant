"""
Shopping Lists Router
API endpoints for managing shopping lists
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..deps import get_current_user_id
from ..schemas.shopping_list import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListOut,
    ShoppingListItemUpdate,
    ShoppingListItemOut,
    GenerateShoppingListRequest
)
from ..services import shopping_list_service

router = APIRouter()


@router.post("/", response_model=ShoppingListOut, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    list_data: ShoppingListCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new shopping list manually"""
    return shopping_list_service.create_shopping_list(db, user_id, list_data)


@router.post("/generate", response_model=ShoppingListOut, status_code=status.HTTP_201_CREATED)
async def generate_shopping_list(
    request_data: GenerateShoppingListRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Generate shopping list from recipes or collection
    Smart merging and auto-categorization
    """
    return shopping_list_service.generate_shopping_list_from_recipes(db, user_id, request_data)


@router.get("/", response_model=List[ShoppingListOut])
async def get_my_shopping_lists(
    skip: int = 0,
    limit: int = 100,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all shopping lists for current user"""
    return shopping_list_service.get_user_shopping_lists(db, user_id, skip, limit)


@router.get("/{list_id}", response_model=ShoppingListOut)
async def get_shopping_list(
    list_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get a specific shopping list"""
    shopping_list = shopping_list_service.get_shopping_list_by_id(db, list_id, user_id)
    if not shopping_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    return shopping_list


@router.put("/{list_id}", response_model=ShoppingListOut)
async def update_shopping_list(
    list_id: int,
    update_data: ShoppingListUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a shopping list"""
    shopping_list = shopping_list_service.update_shopping_list(db, list_id, user_id, update_data)
    if not shopping_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    return shopping_list


@router.patch("/items/{item_id}", response_model=ShoppingListItemOut)
async def toggle_shopping_item(
    item_id: int,
    is_checked: bool,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Toggle shopping list item checked status"""
    item = shopping_list_service.update_shopping_list_item(db, item_id, user_id, is_checked)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a shopping list"""
    success = shopping_list_service.delete_shopping_list(db, list_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
