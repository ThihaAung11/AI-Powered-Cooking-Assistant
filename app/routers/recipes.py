from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut
from ..utils.pagination import PaginationParams, PaginatedResponse
from ..services.recipe_service import create_recipe, get_recipe, list_recipes, update_recipe, delete_recipe
from ..core.security import get_current_user
from ..models import User
from ..deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=RecipeOut)
def create(payload: RecipeCreate, db: SessionDep, current_user: CurrentUser):
    recipe = create_recipe(
        db,
        title=payload.title,
        description=payload.description,
        cuisine=payload.cuisine,
        difficulty=payload.difficulty,
        total_time=payload.total_time,
        ingredients=payload.ingredients,
        image_url=payload.image_url,
        steps=payload.steps,
        user_id=current_user.id,
    )
    return recipe


@router.get("/", response_model=PaginatedResponse[RecipeOut])
def list_all(
    db: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    params = PaginationParams(page=page, page_size=page_size)
    return list_recipes(db, params)


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_one(recipe_id: int, db: SessionDep):
    return get_recipe(db, recipe_id)


@router.put("/{recipe_id}", response_model=RecipeOut)
def update(recipe_id: int, payload: RecipeUpdate, db: SessionDep, current_user: CurrentUser):
    return update_recipe(
        db,
        recipe_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        cuisine=payload.cuisine,
        difficulty=payload.difficulty,
        total_time=payload.total_time,
        ingredients=payload.ingredients,
        image_url=payload.image_url,
        steps=payload.steps,
    )


@router.delete("/{recipe_id}")
def delete(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_recipe(db, recipe_id, user_id=current_user.id)
    return {"detail": "Deleted"}
