from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.recipe import Recipe
from ..exceptions import NotFoundException, UnauthorizedException


def create_recipe(db: Session, *, title: str, description: Optional[str], ingredients: str, steps: str, user_id: int) -> Recipe:
    recipe = Recipe(title=title, description=description, ingredients=ingredients, steps=steps, created_by=user_id)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def get_recipe(db: Session, recipe_id: int) -> Recipe:
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise NotFoundException("Recipe not found")
    return recipe


def list_recipes(db: Session) -> List[Recipe]:
    return db.query(Recipe).all()


def update_recipe(db: Session, recipe_id: int, *, user_id: int, **updates) -> Recipe:
    recipe = get_recipe(db, recipe_id)
    if recipe.created_by != user_id:
        raise UnauthorizedException("You are not allowed to modify this recipe")
    for k, v in updates.items():
        if v is not None:
            setattr(recipe, k, v)
    db.commit()
    db.refresh(recipe)
    return recipe


def delete_recipe(db: Session, recipe_id: int, *, user_id: int) -> None:
    recipe = get_recipe(db, recipe_id)
    if recipe.created_by != user_id:
        raise UnauthorizedException("You are not allowed to delete this recipe")
    db.delete(recipe)
    db.commit()
