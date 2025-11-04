"""
Recipe Collections Router
API endpoints for managing recipe collections and meal planning
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..deps import get_current_user_id
from ..schemas.collection import (
    RecipeCollectionCreate,
    RecipeCollectionUpdate,
    RecipeCollectionOut,
    CollectionItemCreate,
    CollectionItemUpdate,
    CollectionItemOut
)
from ..services import collection_service

router = APIRouter()


@router.post("/", response_model=RecipeCollectionOut, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: RecipeCollectionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new recipe collection"""
    return collection_service.create_collection(db, user_id, collection_data)


@router.get("/", response_model=List[RecipeCollectionOut])
async def get_my_collections(
    skip: int = 0,
    limit: int = 100,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all collections for current user"""
    return collection_service.get_user_collections(db, user_id, skip, limit)


@router.get("/{collection_id}", response_model=RecipeCollectionOut)
async def get_collection(
    collection_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get a specific collection"""
    collection = collection_service.get_collection_by_id(db, collection_id, user_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return collection


@router.put("/{collection_id}", response_model=RecipeCollectionOut)
async def update_collection(
    collection_id: int,
    update_data: RecipeCollectionUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a collection"""
    collection = collection_service.update_collection(db, collection_id, user_id, update_data)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a collection"""
    success = collection_service.delete_collection(db, collection_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")


@router.post("/{collection_id}/recipes", response_model=CollectionItemOut, status_code=status.HTTP_201_CREATED)
async def add_recipe_to_collection(
    collection_id: int,
    item_data: CollectionItemCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Add a recipe to a collection"""
    return collection_service.add_recipe_to_collection(db, collection_id, user_id, item_data)


@router.delete("/{collection_id}/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_recipe_from_collection(
    collection_id: int,
    recipe_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Remove a recipe from a collection"""
    success = collection_service.remove_recipe_from_collection(db, collection_id, recipe_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found in collection")


@router.put("/{collection_id}/items/{item_id}", response_model=CollectionItemOut)
async def update_collection_item(
    collection_id: int,
    item_id: int,
    update_data: CollectionItemUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a collection item (for meal planning metadata)"""
    item = collection_service.update_collection_item(db, collection_id, item_id, user_id, update_data)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item
