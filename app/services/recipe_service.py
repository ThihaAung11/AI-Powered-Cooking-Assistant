from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.recipe import Recipe, CookingStep
from ..schemas.recipe import CookingStepCreate, RecipeOut
from ..utils.pagination import PaginationParams, PaginatedResponse, paginate
from ..exceptions import NotFoundException, UnauthorizedException


def create_recipe(
    db: Session,
    *,
    title: str,
    description: Optional[str],
    cuisine: Optional[str],
    difficulty: Optional[str],
    total_time: Optional[int],
    ingredients: str,
    image_url: Optional[str],
    steps: List[CookingStepCreate],
    user_id: int
) -> Recipe:
    recipe = Recipe(
        title=title,
        description=description,
        cuisine=cuisine,
        difficulty=difficulty,
        total_time=total_time,
        ingredients=ingredients,
        image_url=image_url,
        created_by=user_id
    )
    db.add(recipe)
    db.flush()  # Get recipe.id before adding steps
    
    # Add cooking steps
    for step_data in steps:
        cooking_step = CookingStep(
            recipe_id=recipe.id,
            step_number=step_data.step_number,
            instruction_text=step_data.instruction_text,
            media_url=step_data.media_url
        )
        db.add(cooking_step)
    
    db.commit()
    db.refresh(recipe)
    return recipe


def get_recipe(db: Session, recipe_id: int) -> Recipe:
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise NotFoundException("Recipe not found")
    return recipe


def list_recipes(db: Session, params: Optional[PaginationParams] = None) -> PaginatedResponse[RecipeOut]:
    """List recipes with pagination"""
    query = db.query(Recipe).order_by(Recipe.created_at.desc())
    
    if params is None:
        params = PaginationParams()
    
    return paginate(query, params, RecipeOut)


def update_recipe(db: Session, recipe_id: int, *, user_id: int, **updates) -> Recipe:
    recipe = get_recipe(db, recipe_id)
    if recipe.created_by != user_id:
        raise UnauthorizedException("You are not allowed to modify this recipe")
    
    # Handle steps separately
    steps_data = updates.pop('steps', None)
    
    # Update basic fields
    for k, v in updates.items():
        if v is not None:
            setattr(recipe, k, v)
    
    # Update steps if provided
    if steps_data is not None:
        # Delete existing steps
        db.query(CookingStep).filter(CookingStep.recipe_id == recipe_id).delete()
        
        # Add new steps
        for step_data in steps_data:
            cooking_step = CookingStep(
                recipe_id=recipe.id,
                step_number=step_data.step_number,
                instruction_text=step_data.instruction_text,
                media_url=step_data.media_url
            )
            db.add(cooking_step)
    
    db.commit()
    db.refresh(recipe)
    return recipe


def delete_recipe(db: Session, recipe_id: int, *, user_id: int) -> None:
    recipe = get_recipe(db, recipe_id)
    if recipe.created_by != user_id:
        raise UnauthorizedException("You are not allowed to delete this recipe")
    db.delete(recipe)
    db.commit()
