from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut
from ..services.recipe_service import create_recipe, get_recipe, list_recipes, update_recipe, delete_recipe
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter()


@router.post("/", response_model=RecipeOut)
def create(payload: RecipeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipe = create_recipe(
        db,
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        steps=payload.steps,
        user_id=current_user.id,
    )
    return recipe


@router.get("/", response_model=List[RecipeOut])
def list_all(db: Session = Depends(get_db)):
    return list_recipes(db)


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_one(recipe_id: int, db: Session = Depends(get_db)):
    return get_recipe(db, recipe_id)


@router.put("/{recipe_id}", response_model=RecipeOut)
def update(recipe_id: int, payload: RecipeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_recipe(
        db,
        recipe_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        steps=payload.steps,
    )


@router.delete("/{recipe_id}")
def delete(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_recipe(db, recipe_id, user_id=current_user.id)
    return {"detail": "Deleted"}
