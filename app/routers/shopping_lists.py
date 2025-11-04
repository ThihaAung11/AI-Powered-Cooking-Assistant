"""
Shopping Lists Router
API endpoints for managing shopping lists
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..deps import CurrentUser, SessionDep
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
    current_user: CurrentUser,
    db: SessionDep
):
    """Create a new shopping list manually"""
    user_id = current_user.id
    return shopping_list_service.create_shopping_list(db, user_id, list_data)


@router.post("/generate", response_model=ShoppingListOut, status_code=status.HTTP_201_CREATED)
async def generate_shopping_list(
    request_data: GenerateShoppingListRequest,
    current_user: CurrentUser,
    db: SessionDep
):
    """
    Generate shopping list from recipes or collection
    Smart merging and auto-categorization
    """
    user_id = current_user.id
    return shopping_list_service.generate_shopping_list_from_recipes(db, user_id, request_data)


@router.get("/", response_model=List[ShoppingListOut])
async def get_my_shopping_lists(
    current_user: CurrentUser,
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    """Get all shopping lists for current user"""
    user_id = current_user.id
    return shopping_list_service.get_user_shopping_lists(db, user_id, skip, limit)


@router.get("/{list_id}", response_model=ShoppingListOut)
async def get_shopping_list(
    list_id: int,
    current_user: CurrentUser,
    db: SessionDep
):
    """Get a specific shopping list"""
    user_id = current_user.id
    shopping_list = shopping_list_service.get_shopping_list_by_id(db, list_id, user_id)
    if not shopping_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    return shopping_list


@router.put("/{list_id}", response_model=ShoppingListOut)
async def update_shopping_list(
    list_id: int,
    update_data: ShoppingListUpdate,
    current_user: CurrentUser,
    db: SessionDep
):
    """Update a shopping list"""
    user_id = current_user.id
    shopping_list = shopping_list_service.update_shopping_list(db, list_id, user_id, update_data)
    if not shopping_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    return shopping_list


@router.patch("/items/{item_id}", response_model=ShoppingListItemOut)
async def toggle_shopping_item(
    item_id: int,
    is_checked: bool,
    current_user: CurrentUser,
    db: SessionDep
):
    """Toggle shopping list item checked status"""
    user_id = current_user.id
    item = shopping_list_service.update_shopping_list_item(db, item_id, user_id, is_checked)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: int,
    current_user: CurrentUser,
    db: SessionDep
):
    """Delete a shopping list"""
    user_id = current_user.id
    success = shopping_list_service.delete_shopping_list(db, list_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
