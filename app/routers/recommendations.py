from fastapi import APIRouter, Query
from typing import Optional

from ..schemas.recipe import RecipeOut
from ..services.recommendation_service import (
    get_recommended_recipes,
    get_trending_recipes,
    get_similar_recipes,
    get_recommendation_summary
)
from ..deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/for-me")
def get_recommendations_for_me(
    db: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    max_time: Optional[int] = Query(None, description="Maximum cooking time in minutes")
):
    """
    Get personalized recipe recommendations based on user preferences and history.
    
    Recommendations are based on:
    - User preferences (cuisine, diet, skill level)
    - Cooking history
    - Saved recipes
    - User ratings
    - Recipe popularity
    """
    recommendations = get_recommended_recipes(
        db,
        current_user.id,
        limit=limit,
        cuisine=cuisine,
        difficulty=difficulty,
        max_time=max_time
    )
    
    return {
        "recommendations": [
            {
                "recipe": RecipeOut.model_validate(rec["recipe"]),
                "score": rec["score"],
                "reasons": rec["reasons"]
            }
            for rec in recommendations
        ],
        "total_count": len(recommendations),
        "filters_applied": {
            "cuisine": cuisine,
            "difficulty": difficulty,
            "max_time": max_time
        }
    }


@router.get("/trending")
def get_trending(
    db: SessionDep,
    limit: int = Query(10, ge=1, le=50, description="Number of recipes"),
    days: int = Query(7, ge=1, le=30, description="Number of days to look back")
):
    """
    Get trending recipes based on recent saves and cooking sessions.
    
    Trending is calculated based on:
    - Recent saves
    - Recent cooking sessions
    - Activity in the last N days
    """
    recipes = get_trending_recipes(db, limit=limit, days=days)
    
    return {
        "recipes": [RecipeOut.model_validate(recipe) for recipe in recipes],
        "total_count": len(recipes),
        "period_days": days
    }


@router.get("/similar/{recipe_id}")
def get_similar(
    recipe_id: int,
    db: SessionDep,
    limit: int = Query(5, ge=1, le=20, description="Number of similar recipes")
):
    """
    Get recipes similar to a specific recipe.
    
    Similarity is based on:
    - Same cuisine
    - Same difficulty level
    - Similar cooking time
    """
    recipes = get_similar_recipes(db, recipe_id, limit=limit)
    
    return {
        "recipes": [RecipeOut.model_validate(recipe) for recipe in recipes],
        "total_count": len(recipes),
        "reference_recipe_id": recipe_id
    }


@router.get("/summary")
def get_summary(db: SessionDep, current_user: CurrentUser):
    """
    Get a summary of recommendation factors for the current user.
    
    Provides insights into:
    - User preferences
    - Activity statistics
    - Available recipes matching preferences
    """
    return get_recommendation_summary(db, current_user.id)
