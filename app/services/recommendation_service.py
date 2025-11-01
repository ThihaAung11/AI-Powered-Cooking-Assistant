"""
Recipe Recommendation Service
Provides personalized recipe recommendations based on user preferences and history
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional
from collections import Counter

from ..models.user import User, UserPreference
from ..models.recipe import Recipe
from ..models.user_saved_recipe import UserSavedRecipe
from ..models.user_cooking_session import UserCookingSession
from ..models.user_feedback import UserFeedback
from ..exceptions import NotFoundException


def calculate_recipe_score(
    recipe: Recipe,
    user_prefs: Optional[UserPreference],
    saved_recipe_ids: set,
    cooked_recipe_ids: set,
    highly_rated_recipe_ids: set
) -> tuple[float, List[str]]:
    """
    Calculate recommendation score for a recipe based on multiple factors
    Returns: (score, reasons)
    """
    score = 50.0  # Base score
    reasons = []
    
    # User preference matching
    if user_prefs:
        # Cuisine preference
        if user_prefs.preferred_cuisine and recipe.cuisine:
            if user_prefs.preferred_cuisine.lower() in recipe.cuisine.lower():
                score += 20
                reasons.append(f"Matches your preferred cuisine: {recipe.cuisine}")
        
        # Difficulty matching based on cooking skill
        if user_prefs.cooking_skill:
            skill_difficulty_map = {
                "beginner": "Easy",
                "intermediate": "Medium",
                "advanced": "Hard"
            }
            preferred_difficulty = skill_difficulty_map.get(user_prefs.cooking_skill.lower())
            if preferred_difficulty and recipe.difficulty == preferred_difficulty:
                score += 15
                reasons.append(f"Matches your skill level: {recipe.difficulty}")
        
        # Diet type matching
        if user_prefs.diet_type and recipe.description:
            diet_keywords = {
                "vegetarian": ["vegetarian", "veggie"],
                "vegan": ["vegan"],
                "pescatarian": ["fish", "seafood"],
            }
            diet = user_prefs.diet_type.lower()
            if diet in diet_keywords:
                for keyword in diet_keywords[diet]:
                    if keyword in recipe.description.lower() or keyword in recipe.ingredients.lower():
                        score += 15
                        reasons.append(f"Matches your {diet} diet")
                        break
    
    # Popularity boost (highly rated by others)
    if recipe.id in highly_rated_recipe_ids:
        score += 10
        reasons.append("Highly rated by other users")
    
    # Novelty boost (not saved or cooked before)
    if recipe.id not in saved_recipe_ids and recipe.id not in cooked_recipe_ids:
        score += 5
        reasons.append("New recipe to try")
    
    # Time consideration (prefer recipes under 60 minutes)
    if recipe.total_time and recipe.total_time <= 60:
        score += 5
        reasons.append(f"Quick to make ({recipe.total_time} mins)")
    
    # Penalize if already saved/cooked multiple times
    if recipe.id in saved_recipe_ids:
        score -= 5
    if recipe.id in cooked_recipe_ids:
        cook_count = list(cooked_recipe_ids).count(recipe.id)
        score -= (cook_count * 3)
    
    return (min(100, max(0, score)), reasons)


def get_user_activity_data(db: Session, user_id: int) -> dict:
    """Get user's activity data for recommendations"""
    # Get saved recipe IDs
    saved_recipes = db.query(UserSavedRecipe.recipe_id).filter(
        UserSavedRecipe.user_id == user_id
    ).all()
    saved_recipe_ids = {r.recipe_id for r in saved_recipes}
    
    # Get cooked recipe IDs
    cooked_sessions = db.query(UserCookingSession.recipe_id).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.recipe_id.isnot(None)
    ).all()
    cooked_recipe_ids = [r.recipe_id for r in cooked_sessions]
    
    # Get highly rated recipes (rating >= 4)
    highly_rated = db.query(UserFeedback.recipe_id).filter(
        UserFeedback.user_id == user_id,
        UserFeedback.rating >= 4
    ).all()
    highly_rated_recipe_ids = {r.recipe_id for r in highly_rated}
    
    # Get globally highly rated recipes (avg rating >= 4)
    global_highly_rated = db.query(UserFeedback.recipe_id).group_by(
        UserFeedback.recipe_id
    ).having(
        func.avg(UserFeedback.rating) >= 4
    ).all()
    global_highly_rated_ids = {r.recipe_id for r in global_highly_rated}
    
    return {
        "saved_recipe_ids": saved_recipe_ids,
        "cooked_recipe_ids": cooked_recipe_ids,
        "highly_rated_recipe_ids": highly_rated_recipe_ids,
        "global_highly_rated_ids": global_highly_rated_ids
    }


def get_recommended_recipes(
    db: Session,
    user_id: int,
    limit: int = 10,
    cuisine: Optional[str] = None,
    difficulty: Optional[str] = None,
    max_time: Optional[int] = None
) -> List[dict]:
    """
    Get personalized recipe recommendations for a user
    
    Args:
        db: Database session
        user_id: User ID
        limit: Number of recommendations to return
        cuisine: Optional cuisine filter
        difficulty: Optional difficulty filter
        max_time: Optional max cooking time filter
    
    Returns:
        List of recommended recipes with scores and reasons
    """
    # Get user and preferences
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    
    user_prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    
    # Get user activity data
    activity_data = get_user_activity_data(db, user_id)
    
    # Build base query
    query = db.query(Recipe)
    
    # Apply filters
    if cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))
    elif user_prefs and user_prefs.preferred_cuisine:
        # Prefer user's cuisine but don't restrict to it
        pass
    
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    
    if max_time:
        query = query.filter(Recipe.total_time <= max_time)
    
    # Get recipes (limit to reasonable number for scoring)
    recipes = query.limit(100).all()
    
    # Score each recipe
    scored_recipes = []
    for recipe in recipes:
        score, reasons = calculate_recipe_score(
            recipe,
            user_prefs,
            activity_data["saved_recipe_ids"],
            activity_data["cooked_recipe_ids"],
            activity_data["global_highly_rated_ids"]
        )
        
        scored_recipes.append({
            "recipe": recipe,
            "score": score,
            "reasons": reasons
        })
    
    # Sort by score (descending)
    scored_recipes.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top N
    return scored_recipes[:limit]


def get_trending_recipes(db: Session, limit: int = 10, days: int = 7) -> List[Recipe]:
    """
    Get trending recipes based on recent activity
    
    Args:
        db: Database session
        limit: Number of recipes to return
        days: Number of days to look back
    
    Returns:
        List of trending recipes
    """
    from datetime import datetime, timedelta, timezone
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Count recent saves
    recent_saves = db.query(
        UserSavedRecipe.recipe_id,
        func.count(UserSavedRecipe.id).label('save_count')
    ).filter(
        UserSavedRecipe.created_at >= cutoff_date
    ).group_by(UserSavedRecipe.recipe_id).subquery()
    
    # Count recent cooking sessions
    recent_cooks = db.query(
        UserCookingSession.recipe_id,
        func.count(UserCookingSession.id).label('cook_count')
    ).filter(
        UserCookingSession.started_at >= cutoff_date,
        UserCookingSession.recipe_id.isnot(None)
    ).group_by(UserCookingSession.recipe_id).subquery()
    
    # Get recipes with activity
    trending = db.query(Recipe).outerjoin(
        recent_saves, Recipe.id == recent_saves.c.recipe_id
    ).outerjoin(
        recent_cooks, Recipe.id == recent_cooks.c.recipe_id
    ).order_by(
        desc(func.coalesce(recent_saves.c.save_count, 0) + func.coalesce(recent_cooks.c.cook_count, 0))
    ).limit(limit).all()
    
    return trending


def get_similar_recipes(
    db: Session,
    recipe_id: int,
    limit: int = 5
) -> List[Recipe]:
    """
    Get recipes similar to a given recipe
    
    Args:
        db: Database session
        recipe_id: Recipe ID to find similar recipes for
        limit: Number of similar recipes to return
    
    Returns:
        List of similar recipes
    """
    # Get the reference recipe
    reference_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not reference_recipe:
        raise NotFoundException("Recipe not found")
    
    # Find similar recipes based on cuisine and difficulty
    query = db.query(Recipe).filter(Recipe.id != recipe_id)
    
    if reference_recipe.cuisine:
        query = query.filter(Recipe.cuisine == reference_recipe.cuisine)
    
    if reference_recipe.difficulty:
        query = query.filter(Recipe.difficulty == reference_recipe.difficulty)
    
    # Prefer recipes with similar cooking time
    if reference_recipe.total_time:
        time_range = 15  # minutes
        query = query.filter(
            and_(
                Recipe.total_time >= reference_recipe.total_time - time_range,
                Recipe.total_time <= reference_recipe.total_time + time_range
            )
        )
    
    return query.limit(limit).all()


def get_recommendation_summary(db: Session, user_id: int) -> dict:
    """
    Get a summary of recommendation factors for a user
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Dictionary with recommendation summary
    """
    user_prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    activity_data = get_user_activity_data(db, user_id)
    
    # Count recipes matching user preferences
    total_recipes = db.query(func.count(Recipe.id)).scalar() or 0
    
    matching_cuisine = 0
    if user_prefs and user_prefs.preferred_cuisine:
        matching_cuisine = db.query(func.count(Recipe.id)).filter(
            Recipe.cuisine.ilike(f"%{user_prefs.preferred_cuisine}%")
        ).scalar() or 0
    
    return {
        "total_recipes": total_recipes,
        "saved_recipes": len(activity_data["saved_recipe_ids"]),
        "cooked_recipes": len(set(activity_data["cooked_recipe_ids"])),
        "highly_rated_recipes": len(activity_data["highly_rated_recipe_ids"]),
        "preferred_cuisine": user_prefs.preferred_cuisine if user_prefs else None,
        "matching_cuisine_count": matching_cuisine,
        "cooking_skill": user_prefs.cooking_skill if user_prefs else None,
        "diet_type": user_prefs.diet_type if user_prefs else None
    }
