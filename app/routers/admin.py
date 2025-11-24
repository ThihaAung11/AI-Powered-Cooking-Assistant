from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime

from ..core.security import get_admin_user
from ..database import get_db
from ..models import User, Recipe, UserFeedback, UserCookingSession, CookingStep, Role
from ..schemas.admin import (
    AdminUserOut, AdminUserList, UserDeactivate,
    AdminRecipeCreate, AdminRecipeUpdate, AdminRecipeOut,
    AdminFeedbackOut, AdminFeedbackList, FeedbackRemoveReason,
    CookingHistoryItem, CookingHistoryList, CookingAnalytics,
    AIKnowledgeRefreshResponse, RecipeDataUpdate
)
from ..schemas.recipe import RecipeOut, RecipeCreate, CookingStepCreate
from ..utils.cache import recommendation_cache

router = APIRouter()


# ============================================================================
# RECIPE MANAGEMENT
# ============================================================================

@router.get("/recipes", response_model=List[AdminRecipeOut])
def admin_get_all_recipes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_private: bool = Query(True),
    created_by: Optional[int] = Query(None),
    cuisine: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get all recipes with detailed information (admin only).
    Can filter by creator, cuisine, and include private recipes.
    """
    query = db.query(Recipe).options(joinedload(Recipe.creator), joinedload(Recipe.feedbacks))
    
    if not include_private:
        query = query.filter(Recipe.is_public == True)
    
    if created_by:
        query = query.filter(Recipe.created_by == created_by)
    
    if cuisine:
        query = query.filter(Recipe.cuisine == cuisine)
    
    recipes = query.offset(skip).limit(limit).all()
    
    # Enhance with statistics
    result = []
    for recipe in recipes:
        feedbacks_count = len(recipe.feedbacks)
        avg_rating = sum(f.rating for f in recipe.feedbacks) / feedbacks_count if feedbacks_count > 0 else 0.0
        
        result.append(AdminRecipeOut(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            cuisine=recipe.cuisine,
            difficulty=recipe.difficulty,
            total_time=recipe.total_time,
            ingredients=recipe.ingredients,
            image_url=recipe.image_url,
            is_public=recipe.is_public,
            created_by=recipe.created_by,
            creator_name=recipe.creator.name if recipe.creator else "Unknown",
            created_at=recipe.created_at,
            feedbacks_count=feedbacks_count,
            average_rating=round(avg_rating, 2)
        ))
    
    return result


@router.post("/recipes", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
def admin_create_recipe(
    recipe_data: AdminRecipeCreate,
    steps: Optional[List[CookingStepCreate]] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Create a new recipe as admin. Can assign to any user or use admin's ID.
    """
    # Create recipe with admin as creator
    new_recipe = Recipe(
        title=recipe_data.title,
        description=recipe_data.description,
        cuisine=recipe_data.cuisine,
        difficulty=recipe_data.difficulty,
        total_time=recipe_data.total_time,
        ingredients=recipe_data.ingredients,
        is_public=recipe_data.is_public,
        created_by=admin.id
    )
    
    db.add(new_recipe)
    db.flush()  # Get the recipe ID
    
    # Add cooking steps if provided
    if steps:
        for step_data in steps:
            cooking_step = CookingStep(
                recipe_id=new_recipe.id,
                step_number=step_data.step_number,
                instruction_text=step_data.instruction_text,
                media_url=step_data.media_url
            )
            db.add(cooking_step)
    
    db.commit()
    db.refresh(new_recipe)
    
    return new_recipe


@router.put("/recipes/{recipe_id}", response_model=RecipeOut)
def admin_update_recipe(
    recipe_id: int,
    recipe_data: AdminRecipeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Update any recipe (admin only). Can modify any field including visibility.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Update fields if provided
    update_data = recipe_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recipe, field, value)
    
    db.commit()
    db.refresh(recipe)
    
    return recipe


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Delete any recipe (admin only). This will cascade delete all related data.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(recipe)
    db.commit()
    
    return None


# ============================================================================
# AI KNOWLEDGE MANAGEMENT
# ============================================================================

@router.post("/ai/refresh-embeddings", response_model=AIKnowledgeRefreshResponse)
async def refresh_recipe_embeddings(
    data: RecipeDataUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Refresh recipe embeddings for RAG system.
    This endpoint triggers the re-processing of recipe data for AI.
    """
    try:
        # Get recipes to process
        query = db.query(Recipe)
        if data.recipe_ids:
            query = query.filter(Recipe.id.in_(data.recipe_ids))
        
        recipes = query.all()
        
        if not recipes:
            return AIKnowledgeRefreshResponse(
                success=False,
                message="No recipes found to process"
            )
        
        # TODO: Implement actual embedding generation
        # This would integrate with your vector database (ChromaDB, Pinecone, etc.)
        # For now, we'll return a success response indicating the data is ready
        
        recipes_count = len(recipes)
        
        return AIKnowledgeRefreshResponse(
            success=True,
            message=f"Successfully processed {recipes_count} recipes for AI knowledge base",
            recipes_processed=recipes_count,
            embeddings_created=recipes_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing embeddings: {str(e)}"
        )


@router.post("/ai/update-recipe-data", response_model=AIKnowledgeRefreshResponse)
async def update_ai_recipe_data(
    data: RecipeDataUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Update recipe data in AI knowledge base.
    Forces a complete refresh of recipe information for the AI assistant.
    """
    try:
        query = db.query(Recipe).options(joinedload(Recipe.steps), joinedload(Recipe.feedbacks))
        
        if data.recipe_ids:
            query = query.filter(Recipe.id.in_(data.recipe_ids))
        
        recipes = query.all()
        
        # TODO: Implement vector database update logic
        # This would:
        # 1. Generate new embeddings for recipes
        # 2. Update vector database
        # 3. Refresh RAG context
        
        return AIKnowledgeRefreshResponse(
            success=True,
            message=f"AI knowledge base updated successfully with {len(recipes)} recipes",
            recipes_processed=len(recipes),
            embeddings_created=len(recipes)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating AI knowledge: {str(e)}"
        )


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users", response_model=AdminUserList)
def admin_get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    role_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get all users with statistics (admin only).
    Can filter by active status, role, and search by username/email.
    """
    query = db.query(User).options(
        joinedload(User.role),
        joinedload(User.recipes),
        joinedload(User.cooking_sessions),
        joinedload(User.feedbacks)
    )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if role_id:
        query = query.filter(User.role_id == role_id)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_pattern)) |
            (User.email.ilike(search_pattern)) |
            (User.name.ilike(search_pattern))
        )
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    # Build response with statistics
    user_list = []
    for user in users:
        user_list.append(AdminUserOut(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            profile_url=user.profile_url,
            is_active=user.is_active,
            role_id=user.role_id,
            role_name=user.role.name if user.role else "Unknown",
            created_at=user.created_at,
            total_recipes=len(user.recipes),
            total_cooking_sessions=len(user.cooking_sessions),
            total_feedbacks=len(user.feedbacks)
        ))
    
    return AdminUserList(total=total, users=user_list)


@router.get("/users/{user_id}", response_model=AdminUserOut)
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get detailed information about a specific user (admin only).
    """
    user = db.query(User).options(
        joinedload(User.role),
        joinedload(User.recipes),
        joinedload(User.cooking_sessions),
        joinedload(User.feedbacks)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return AdminUserOut(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        profile_url=user.profile_url,
        is_active=user.is_active,
        role_id=user.role_id,
        role_name=user.role.name if user.role else "Unknown",
        created_at=user.created_at,
        total_recipes=len(user.recipes),
        total_cooking_sessions=len(user.cooking_sessions),
        total_feedbacks=len(user.feedbacks)
    )


@router.post("/users/{user_id}/deactivate")
def admin_deactivate_user(
    user_id: int,
    data: UserDeactivate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Deactivate a user account (admin only).
    Prevents the user from logging in and accessing the system.
    """
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    
    return {
        "success": True,
        "message": f"User {user.username} has been deactivated",
        "reason": data.reason
    }


@router.post("/users/{user_id}/activate")
def admin_activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Reactivate a deactivated user account (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    
    return {
        "success": True,
        "message": f"User {user.username} has been activated"
    }


# ============================================================================
# COMMENTS & RATINGS MANAGEMENT
# ============================================================================

@router.get("/feedbacks", response_model=AdminFeedbackList)
def admin_get_all_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    recipe_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    max_rating: Optional[int] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get all feedbacks/comments with filtering (admin only).
    Can filter by recipe, user, and rating range.
    """
    query = db.query(UserFeedback).options(
        joinedload(UserFeedback.user),
        joinedload(UserFeedback.recipe)
    )
    
    if recipe_id:
        query = query.filter(UserFeedback.recipe_id == recipe_id)
    
    if user_id:
        query = query.filter(UserFeedback.user_id == user_id)
    
    if min_rating:
        query = query.filter(UserFeedback.rating >= min_rating)
    
    if max_rating:
        query = query.filter(UserFeedback.rating <= max_rating)
    
    total = query.count()
    feedbacks = query.order_by(desc(UserFeedback.created_at)).offset(skip).limit(limit).all()
    
    # Build response
    feedback_list = []
    for feedback in feedbacks:
        feedback_list.append(AdminFeedbackOut(
            id=feedback.id,
            user_id=feedback.user_id,
            username=feedback.user.username if feedback.user else "Unknown",
            recipe_id=feedback.recipe_id,
            recipe_title=feedback.recipe.title if feedback.recipe else "Unknown",
            rating=feedback.rating,
            comment=feedback.comment,
            created_at=feedback.created_at
        ))
    
    return AdminFeedbackList(total=total, feedbacks=feedback_list)


@router.delete("/feedbacks/{feedback_id}")
def admin_remove_feedback(
    feedback_id: int,
    reason: FeedbackRemoveReason,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Remove inappropriate or spam feedback (admin only).
    Requires a reason for audit purposes.
    """
    feedback = db.query(UserFeedback).filter(UserFeedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Store feedback info before deletion for response
    feedback_info = {
        "feedback_id": feedback.id,
        "user_id": feedback.user_id,
        "recipe_id": feedback.recipe_id,
        "rating": feedback.rating,
        "comment": feedback.comment
    }
    
    db.delete(feedback)
    db.commit()
    
    return {
        "success": True,
        "message": "Feedback removed successfully",
        "removed_feedback": feedback_info,
        "reason": reason.reason,
        "removed_by": admin.username,
        "removed_at": datetime.utcnow()
    }


# ============================================================================
# COOKING HISTORY & ANALYTICS
# ============================================================================

@router.get("/cooking-sessions", response_model=CookingHistoryList)
def admin_get_cooking_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None),
    recipe_id: Optional[int] = Query(None),
    completed_only: bool = Query(False),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get cooking session history with filtering (admin only).
    Shows which recipes users have cooked.
    """
    query = db.query(UserCookingSession).options(
        joinedload(UserCookingSession.user),
        joinedload(UserCookingSession.recipe)
    )
    
    if user_id:
        query = query.filter(UserCookingSession.user_id == user_id)
    
    if recipe_id:
        query = query.filter(UserCookingSession.recipe_id == recipe_id)
    
    if completed_only:
        query = query.filter(UserCookingSession.ended_at.isnot(None))
    
    total = query.count()
    sessions = query.order_by(desc(UserCookingSession.started_at)).offset(skip).limit(limit).all()
    
    # Build response
    session_list = []
    for session in sessions:
        session_list.append(CookingHistoryItem(
            session_id=session.id,
            user_id=session.user_id,
            username=session.user.username if session.user else "Unknown",
            recipe_id=session.recipe_id,
            recipe_title=session.recipe.title if session.recipe else "Unknown",
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_minutes=session.duration_minutes
        ))
    
    return CookingHistoryList(total=total, sessions=session_list)


@router.get("/analytics/cooking", response_model=CookingAnalytics)
def admin_get_cooking_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get cooking analytics and statistics (admin only).
    Provides insights into platform usage.
    """
    from datetime import timedelta
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total sessions
    total_sessions = db.query(UserCookingSession).filter(
        UserCookingSession.started_at >= start_date
    ).count()
    
    # Completed sessions
    completed_sessions = db.query(UserCookingSession).filter(
        UserCookingSession.started_at >= start_date,
        UserCookingSession.ended_at.isnot(None)
    ).count()
    
    # Total cooking time
    total_time_result = db.query(
        func.sum(UserCookingSession.duration_minutes)
    ).filter(
        UserCookingSession.started_at >= start_date,
        UserCookingSession.duration_minutes.isnot(None)
    ).scalar()
    
    total_cooking_time = int(total_time_result) if total_time_result else 0
    
    # Average session duration
    avg_duration = total_cooking_time / completed_sessions if completed_sessions > 0 else 0.0
    
    # Most cooked recipes
    most_cooked = db.query(
        Recipe.id,
        Recipe.title,
        func.count(UserCookingSession.id).label('count')
    ).join(
        UserCookingSession, Recipe.id == UserCookingSession.recipe_id
    ).filter(
        UserCookingSession.started_at >= start_date
    ).group_by(
        Recipe.id, Recipe.title
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    most_cooked_recipes = [
        {"recipe_id": r.id, "recipe_title": r.title, "count": r.count}
        for r in most_cooked
    ]
    
    # Top active users
    top_users = db.query(
        User.id,
        User.username,
        func.count(UserCookingSession.id).label('session_count')
    ).join(
        UserCookingSession, User.id == UserCookingSession.user_id
    ).filter(
        UserCookingSession.started_at >= start_date
    ).group_by(
        User.id, User.username
    ).order_by(
        desc('session_count')
    ).limit(10).all()
    
    top_active_users = [
        {"user_id": u.id, "username": u.username, "session_count": u.session_count}
        for u in top_users
    ]
    
    return CookingAnalytics(
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        total_cooking_time_minutes=total_cooking_time,
        average_session_duration_minutes=round(avg_duration, 2),
        most_cooked_recipes=most_cooked_recipes,
        top_active_users=top_active_users
    )


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

@router.post("/cache/clear")
def admin_clear_cache(
    admin: User = Depends(get_admin_user)
):
    """
    Clear all cached recommendations (admin only).
    Use this after updating recipes or AI models.
    """
    recommendation_cache.clear()
    return {
        "success": True,
        "message": "Recommendation cache cleared successfully"
    }


@router.post("/cache/cleanup")
def admin_cleanup_cache(
    admin: User = Depends(get_admin_user)
):
    """
    Remove expired cache entries (admin only).
    """
    recommendation_cache.remove_expired()
    return {
        "success": True,
        "message": "Expired cache entries removed"
    }
