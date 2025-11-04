"""
Recipe Collection Service
Handles recipe collections and meal planning features
"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from fastapi import HTTPException, status

from ..models import RecipeCollection, CollectionItem, Recipe
from ..schemas.collection import (
    RecipeCollectionCreate,
    RecipeCollectionUpdate,
    CollectionItemCreate,
    CollectionItemUpdate
)


def create_collection(db: Session, user_id: int, collection_data: RecipeCollectionCreate) -> RecipeCollection:
    """Create a new recipe collection"""
    collection = RecipeCollection(
        user_id=user_id,
        name=collection_data.name,
        description=collection_data.description,
        collection_type=collection_data.collection_type,
        is_public=collection_data.is_public
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def get_user_collections(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[RecipeCollection]:
    """Get all collections for a user"""
    return db.query(RecipeCollection)\
        .filter(RecipeCollection.user_id == user_id)\
        .options(joinedload(RecipeCollection.items).joinedload(CollectionItem.recipe))\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_collection_by_id(db: Session, collection_id: int, user_id: Optional[int] = None) -> Optional[RecipeCollection]:
    """Get collection by ID with permission check"""
    query = db.query(RecipeCollection)\
        .options(joinedload(RecipeCollection.items).joinedload(CollectionItem.recipe))\
        .filter(RecipeCollection.id == collection_id)
    
    collection = query.first()
    
    if not collection:
        return None
    
    # Permission check: must be owner or public
    if user_id and collection.user_id != user_id and not collection.is_public:
        return None
    
    return collection


def update_collection(
    db: Session,
    collection_id: int,
    user_id: int,
    update_data: RecipeCollectionUpdate
) -> Optional[RecipeCollection]:
    """Update collection (owner only)"""
    collection = db.query(RecipeCollection)\
        .filter(RecipeCollection.id == collection_id, RecipeCollection.user_id == user_id)\
        .first()
    
    if not collection:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(collection, key, value)
    
    db.commit()
    db.refresh(collection)
    return collection


def delete_collection(db: Session, collection_id: int, user_id: int) -> bool:
    """Delete collection (owner only)"""
    collection = db.query(RecipeCollection)\
        .filter(RecipeCollection.id == collection_id, RecipeCollection.user_id == user_id)\
        .first()
    
    if not collection:
        return False
    
    db.delete(collection)
    db.commit()
    return True


def add_recipe_to_collection(
    db: Session,
    collection_id: int,
    user_id: int,
    item_data: CollectionItemCreate
) -> Optional[CollectionItem]:
    """Add a recipe to a collection"""
    # Verify collection ownership
    collection = db.query(RecipeCollection)\
        .filter(RecipeCollection.id == collection_id, RecipeCollection.user_id == user_id)\
        .first()
    
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    
    # Verify recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == item_data.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    # Check if already exists
    existing = db.query(CollectionItem)\
        .filter(
            CollectionItem.collection_id == collection_id,
            CollectionItem.recipe_id == item_data.recipe_id
        )\
        .first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipe already in collection")
    
    # Create item
    item = CollectionItem(
        collection_id=collection_id,
        recipe_id=item_data.recipe_id,
        order=item_data.order,
        day_of_week=item_data.day_of_week,
        meal_type=item_data.meal_type,
        notes=item_data.notes,
        servings=item_data.servings
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_recipe_from_collection(
    db: Session,
    collection_id: int,
    recipe_id: int,
    user_id: int
) -> bool:
    """Remove a recipe from a collection"""
    # Verify ownership
    collection = db.query(RecipeCollection)\
        .filter(RecipeCollection.id == collection_id, RecipeCollection.user_id == user_id)\
        .first()
    
    if not collection:
        return False
    
    # Find and delete item
    item = db.query(CollectionItem)\
        .filter(
            CollectionItem.collection_id == collection_id,
            CollectionItem.recipe_id == recipe_id
        )\
        .first()
    
    if not item:
        return False
    
    db.delete(item)
    db.commit()
    return True


def update_collection_item(
    db: Session,
    collection_id: int,
    item_id: int,
    user_id: int,
    update_data: CollectionItemUpdate
) -> Optional[CollectionItem]:
    """Update a collection item (meal planning metadata)"""
    # Verify ownership
    collection = db.query(RecipeCollection)\
        .filter(RecipeCollection.id == collection_id, RecipeCollection.user_id == user_id)\
        .first()
    
    if not collection:
        return None
    
    item = db.query(CollectionItem)\
        .filter(CollectionItem.id == item_id, CollectionItem.collection_id == collection_id)\
        .first()
    
    if not item:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item
