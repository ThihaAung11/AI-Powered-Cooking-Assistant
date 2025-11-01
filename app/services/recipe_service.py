from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional

from ..models.recipe import Recipe, CookingStep
from ..schemas.recipe import CookingStepCreate, RecipeOut, RecipeSearchFilter
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
    is_public: bool,
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
        is_public=is_public,
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
    """List public recipes with pagination"""
    query = db.query(Recipe).filter(Recipe.is_public == True).order_by(Recipe.created_at.desc())
    
    if params is None:
        params = PaginationParams()
    
    return paginate(query, params, RecipeOut)


def search_recipes(
    db: Session,
    filters: RecipeSearchFilter,
    current_user_id: Optional[int] = None,
    params: Optional[PaginationParams] = None
) -> PaginatedResponse[RecipeOut]:
    """Search and filter recipes with advanced options"""
    query = db.query(Recipe)
    
    # Public visibility filter
    if filters.include_private and current_user_id:
        # Show public recipes + user's own private recipes
        query = query.filter(
            or_(
                Recipe.is_public == True,
                and_(Recipe.is_public == False, Recipe.created_by == current_user_id)
            )
        )
    else:
        # Only show public recipes
        query = query.filter(Recipe.is_public == True)
    
    # Search in title, description, and ingredients
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Recipe.title.ilike(search_term),
                Recipe.description.ilike(search_term),
                Recipe.ingredients.ilike(search_term)
            )
        )
    
    # Filter by cuisine
    if filters.cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{filters.cuisine}%"))
    
    # Filter by difficulty
    if filters.difficulty:
        query = query.filter(Recipe.difficulty.ilike(f"%{filters.difficulty}%"))
    
    # Filter by cooking time range
    if filters.min_time is not None:
        query = query.filter(Recipe.total_time >= filters.min_time)
    
    if filters.max_time is not None:
        query = query.filter(Recipe.total_time <= filters.max_time)
    
    # Filter by specific ingredients
    if filters.ingredients:
        ingredient_term = f"%{filters.ingredients}%"
        query = query.filter(Recipe.ingredients.ilike(ingredient_term))
    
    # Filter by creator
    if filters.created_by:
        query = query.filter(Recipe.created_by == filters.created_by)
    
    # Order by most recent
    query = query.order_by(Recipe.created_at.desc())
    
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
