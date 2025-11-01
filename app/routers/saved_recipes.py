from fastapi import APIRouter, Query, status

from ..schemas.saved_recipe import SavedRecipeCreate, SavedRecipeOut, SavedRecipeWithDetails
from ..utils.pagination import PaginationParams, PaginatedResponse
from ..services.saved_recipe_service import (
    save_recipe,
    unsave_recipe,
    is_recipe_saved,
    get_saved_recipe,
    list_user_saved_recipes,
    list_recipe_saves,
    get_saved_recipe_count,
    delete_saved_recipe
)
from ..deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=SavedRecipeOut, status_code=status.HTTP_201_CREATED)
def save(payload: SavedRecipeCreate, db: SessionDep, current_user: CurrentUser):
    """Save a recipe to user's collection"""
    return save_recipe(
        db,
        recipe_id=payload.recipe_id,
        user_id=current_user.id
    )


@router.delete("/recipe/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave(recipe_id: int, db: SessionDep, current_user: CurrentUser):
    """Remove a recipe from user's saved collection"""
    unsave_recipe(db, recipe_id=recipe_id, user_id=current_user.id)
    return None


@router.get("/recipe/{recipe_id}/is-saved")
def check_saved(recipe_id: int, db: SessionDep, current_user: CurrentUser):
    """Check if a recipe is saved by the current user"""
    return {"is_saved": is_recipe_saved(db, current_user.id, recipe_id)}


@router.get("/my-saved-recipes", response_model=PaginatedResponse[SavedRecipeWithDetails])
def list_my_saved(
    db: SessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    include_details: bool = Query(True, description="Include full recipe details")
):
    """List current user's saved recipes"""
    params = PaginationParams(page=page, page_size=page_size)
    return list_user_saved_recipes(db, current_user.id, params, include_details=include_details)


@router.get("/recipe/{recipe_id}/saves", response_model=PaginatedResponse[SavedRecipeOut])
def list_recipe_save(
    recipe_id: int,
    db: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """List all users who saved a specific recipe"""
    params = PaginationParams(page=page, page_size=page_size)
    return list_recipe_saves(db, recipe_id, params)


@router.get("/recipe/{recipe_id}/save-count")
def get_save_count(recipe_id: int, db: SessionDep):
    """Get the number of times a recipe has been saved"""
    count = get_saved_recipe_count(db, recipe_id)
    return {"recipe_id": recipe_id, "save_count": count}


@router.get("/{saved_recipe_id}", response_model=SavedRecipeOut)
def get_one(saved_recipe_id: int, db: SessionDep):
    """Get a specific saved recipe by ID"""
    return get_saved_recipe(db, saved_recipe_id)


@router.delete("/{saved_recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(saved_recipe_id: int, db: SessionDep, current_user: CurrentUser):
    """Delete a saved recipe entry"""
    delete_saved_recipe(db, saved_recipe_id, user_id=current_user.id)
    return None
