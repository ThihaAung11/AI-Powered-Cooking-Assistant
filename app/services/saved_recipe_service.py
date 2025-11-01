from sqlalchemy.orm import Session, joinedload
from typing import Optional

from ..models.user_saved_recipe import UserSavedRecipe
from ..models.recipe import Recipe
from ..schemas.saved_recipe import SavedRecipeOut, SavedRecipeWithDetails
from ..utils.pagination import PaginationParams, PaginatedResponse, paginate
from ..exceptions import NotFoundException, BadRequestException, UnauthorizedException


def save_recipe(
    db: Session,
    *,
    recipe_id: int,
    user_id: int
) -> UserSavedRecipe:
    """Save a recipe to user's collection"""
    # Verify recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise NotFoundException("Recipe not found")
    
    # Check if already saved
    existing = db.query(UserSavedRecipe).filter(
        UserSavedRecipe.user_id == user_id,
        UserSavedRecipe.recipe_id == recipe_id
    ).first()
    
    if existing:
        raise BadRequestException("Recipe is already saved")
    
    saved_recipe = UserSavedRecipe(
        user_id=user_id,
        recipe_id=recipe_id
    )
    db.add(saved_recipe)
    db.commit()
    db.refresh(saved_recipe)
    return saved_recipe


def unsave_recipe(
    db: Session,
    *,
    recipe_id: int,
    user_id: int
) -> None:
    """Remove a recipe from user's saved collection"""
    saved_recipe = db.query(UserSavedRecipe).filter(
        UserSavedRecipe.user_id == user_id,
        UserSavedRecipe.recipe_id == recipe_id
    ).first()
    
    if not saved_recipe:
        raise NotFoundException("Saved recipe not found")
    
    db.delete(saved_recipe)
    db.commit()


def is_recipe_saved(db: Session, user_id: int, recipe_id: int) -> bool:
    """Check if a recipe is saved by the user"""
    return db.query(UserSavedRecipe).filter(
        UserSavedRecipe.user_id == user_id,
        UserSavedRecipe.recipe_id == recipe_id
    ).first() is not None


def get_saved_recipe(db: Session, saved_recipe_id: int) -> UserSavedRecipe:
    """Get a specific saved recipe by ID"""
    saved_recipe = db.query(UserSavedRecipe).filter(
        UserSavedRecipe.id == saved_recipe_id
    ).first()
    
    if not saved_recipe:
        raise NotFoundException("Saved recipe not found")
    
    return saved_recipe


def list_user_saved_recipes(
    db: Session,
    user_id: int,
    params: Optional[PaginationParams] = None,
    include_details: bool = False
) -> PaginatedResponse:
    """List user's saved recipes with pagination"""
    query = db.query(UserSavedRecipe).filter(
        UserSavedRecipe.user_id == user_id
    )
    
    if include_details:
        query = query.options(joinedload(UserSavedRecipe.recipe))
    
    query = query.order_by(UserSavedRecipe.created_at.desc())
    
    if params is None:
        params = PaginationParams()
    
    model_class = SavedRecipeWithDetails if include_details else SavedRecipeOut
    return paginate(query, params, model_class)


def list_recipe_saves(
    db: Session,
    recipe_id: int,
    params: Optional[PaginationParams] = None
) -> PaginatedResponse[SavedRecipeOut]:
    """List all users who saved a specific recipe"""
    # Verify recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise NotFoundException("Recipe not found")
    
    query = db.query(UserSavedRecipe).filter(
        UserSavedRecipe.recipe_id == recipe_id
    ).order_by(UserSavedRecipe.created_at.desc())
    
    if params is None:
        params = PaginationParams()
    
    return paginate(query, params, SavedRecipeOut)


def get_saved_recipe_count(db: Session, recipe_id: int) -> int:
    """Get the number of times a recipe has been saved"""
    return db.query(UserSavedRecipe).filter(
        UserSavedRecipe.recipe_id == recipe_id
    ).count()


def delete_saved_recipe(db: Session, saved_recipe_id: int, *, user_id: int) -> None:
    """Delete a saved recipe entry"""
    saved_recipe = get_saved_recipe(db, saved_recipe_id)
    
    if saved_recipe.user_id != user_id:
        raise UnauthorizedException("You are not allowed to delete this saved recipe")
    
    db.delete(saved_recipe)
    db.commit()
