from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.recipe import Recipe
from ..models.user_saved_recipe import UserSavedRecipe
from ..schemas.recipe import RecipeOut


def enrich_recipes_with_saved_status(
    db: Session,
    recipes: Union[List[Recipe], Recipe],
    user_id: Optional[int] = None
) -> Union[List[RecipeOut], RecipeOut]:
    """
    Enrich recipe(s) with saved status and save count information.
    
    Args:
        db: Database session
        recipes: Single recipe or list of recipes
        user_id: Current user ID (optional, for checking saved status)
        
    Returns:
        Enriched recipe(s) with is_saved and save_count fields
    """
    # Handle single recipe
    if isinstance(recipes, Recipe):
        return _enrich_single_recipe(db, recipes, user_id)
    
    # Handle list of recipes
    if not recipes:
        return []
    
    recipe_ids = [recipe.id for recipe in recipes]
    
    # Get save counts for all recipes in one query
    save_counts = dict(
        db.query(UserSavedRecipe.recipe_id, func.count(UserSavedRecipe.id))
        .filter(UserSavedRecipe.recipe_id.in_(recipe_ids))
        .group_by(UserSavedRecipe.recipe_id)
        .all()
    )
    
    # Get saved status for current user (if authenticated)
    user_saved_recipes = set()
    if user_id:
        user_saved_recipes = {
            saved.recipe_id
            for saved in db.query(UserSavedRecipe.recipe_id)
            .filter(
                UserSavedRecipe.user_id == user_id,
                UserSavedRecipe.recipe_id.in_(recipe_ids)
            )
            .all()
        }
    
    # Create enriched recipes
    enriched_recipes = []
    for recipe in recipes:
        # Convert recipe to dict properly including relationships
        recipe_data = {
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'cuisine': recipe.cuisine,
            'difficulty': recipe.difficulty,
            'total_time': recipe.total_time,
            'ingredients': recipe.ingredients,
            'image_url': recipe.image_url,
            'is_public': recipe.is_public,
            'created_by': recipe.created_by,
            'created_at': recipe.created_at,
            'updated_at': recipe.updated_at,
            'steps': recipe.steps,
            'creator': recipe.creator,
            'is_saved': recipe.id in user_saved_recipes if user_id else None,
            'save_count': save_counts.get(recipe.id, 0)
        }
        
        enriched_recipes.append(RecipeOut.model_validate(recipe_data))
    
    return enriched_recipes


def _enrich_single_recipe(
    db: Session,
    recipe: Recipe,
    user_id: Optional[int] = None
) -> RecipeOut:
    """Enrich a single recipe with saved status and save count."""
    
    # Get save count
    save_count = db.query(func.count(UserSavedRecipe.id)).filter(
        UserSavedRecipe.recipe_id == recipe.id
    ).scalar() or 0
    
    # Check if saved by current user
    is_saved = None
    if user_id:
        is_saved = db.query(UserSavedRecipe).filter(
            UserSavedRecipe.user_id == user_id,
            UserSavedRecipe.recipe_id == recipe.id
        ).first() is not None
    
    # Create enriched recipe with all data including relationships
    recipe_data = {
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'cuisine': recipe.cuisine,
        'difficulty': recipe.difficulty,
        'total_time': recipe.total_time,
        'ingredients': recipe.ingredients,
        'image_url': recipe.image_url,
        'is_public': recipe.is_public,
        'created_by': recipe.created_by,
        'created_at': recipe.created_at,
        'updated_at': recipe.updated_at,
        'steps': recipe.steps,
        'creator': recipe.creator,
        'is_saved': is_saved,
        'save_count': save_count
    }
    
    return RecipeOut.model_validate(recipe_data)


def check_recipes_saved_status(
    db: Session,
    recipe_ids: List[int],
    user_id: int
) -> dict[int, bool]:
    """
    Check saved status for multiple recipes at once.
    
    Args:
        db: Database session
        recipe_ids: List of recipe IDs to check
        user_id: User ID to check saved status for
        
    Returns:
        Dictionary mapping recipe_id -> is_saved boolean
    """
    if not recipe_ids:
        return {}
    
    saved_recipe_ids = {
        saved.recipe_id
        for saved in db.query(UserSavedRecipe.recipe_id)
        .filter(
            UserSavedRecipe.user_id == user_id,
            UserSavedRecipe.recipe_id.in_(recipe_ids)
        )
        .all()
    }
    
    return {
        recipe_id: recipe_id in saved_recipe_ids
        for recipe_id in recipe_ids
    }


def get_recipe_save_counts(
    db: Session,
    recipe_ids: List[int]
) -> dict[int, int]:
    """
    Get save counts for multiple recipes at once.
    
    Args:
        db: Database session
        recipe_ids: List of recipe IDs to get counts for
        
    Returns:
        Dictionary mapping recipe_id -> save_count
    """
    if not recipe_ids:
        return {}
    
    save_counts = dict(
        db.query(UserSavedRecipe.recipe_id, func.count(UserSavedRecipe.id))
        .filter(UserSavedRecipe.recipe_id.in_(recipe_ids))
        .group_by(UserSavedRecipe.recipe_id)
        .all()
    )
    
    # Ensure all recipe IDs are present (with 0 count if not saved)
    return {
        recipe_id: save_counts.get(recipe_id, 0)
        for recipe_id in recipe_ids
    }
