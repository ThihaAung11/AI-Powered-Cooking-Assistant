"""
User Profile Service
Manage user profile information and statistics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from ..models.user import User
from ..models.recipe import Recipe
from ..models.user_saved_recipe import UserSavedRecipe
from ..models.user_cooking_session import UserCookingSession
from ..models.user_feedback import UserFeedback
from ..core.security import get_password_hash, verify_password
from ..exceptions import NotFoundException, BadRequestException, UnauthorizedException


def get_user_profile(db: Session, user_id: int) -> dict:
    """Get user profile with basic statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    
    # Get statistics
    total_recipes = db.query(func.count(Recipe.id)).filter(Recipe.created_by == user_id).scalar() or 0
    total_saved = db.query(func.count(UserSavedRecipe.id)).filter(UserSavedRecipe.user_id == user_id).scalar() or 0
    total_sessions = db.query(func.count(UserCookingSession.id)).filter(UserCookingSession.user_id == user_id).scalar() or 0
    total_feedbacks = db.query(func.count(UserFeedback.id)).filter(UserFeedback.user_id == user_id).scalar() or 0
    
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "profile_url": user.profile_url,
        "is_active": user.is_active,
        "role_id": user.role_id,
        "total_recipes": total_recipes,
        "total_saved_recipes": total_saved,
        "total_cooking_sessions": total_sessions,
        "total_feedbacks": total_feedbacks
    }


def get_user_stats(db: Session, user_id: int) -> dict:
    """Get detailed user statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    
    # Recipes created
    total_recipes_created = db.query(func.count(Recipe.id)).filter(
        Recipe.created_by == user_id
    ).scalar() or 0
    
    # Recipes saved
    total_recipes_saved = db.query(func.count(UserSavedRecipe.id)).filter(
        UserSavedRecipe.user_id == user_id
    ).scalar() or 0
    
    # Cooking sessions
    total_sessions = db.query(func.count(UserCookingSession.id)).filter(
        UserCookingSession.user_id == user_id
    ).scalar() or 0
    
    completed_sessions = db.query(func.count(UserCookingSession.id)).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.ended_at.isnot(None)
    ).scalar() or 0
    
    total_minutes = db.query(func.sum(UserCookingSession.duration_minutes)).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.duration_minutes.isnot(None)
    ).scalar() or 0
    
    # Feedbacks given
    total_feedbacks_given = db.query(func.count(UserFeedback.id)).filter(
        UserFeedback.user_id == user_id
    ).scalar() or 0
    
    avg_rating_given = db.query(func.avg(UserFeedback.rating)).filter(
        UserFeedback.user_id == user_id
    ).scalar() or 0.0
    
    # Feedbacks received on user's recipes
    recipes_feedback_stats = db.query(
        func.count(UserFeedback.id).label('count'),
        func.avg(UserFeedback.rating).label('avg_rating')
    ).join(Recipe, UserFeedback.recipe_id == Recipe.id).filter(
        Recipe.created_by == user_id
    ).first()
    
    recipes_received_feedbacks = recipes_feedback_stats.count if recipes_feedback_stats else 0
    avg_rating_received = float(recipes_feedback_stats.avg_rating) if recipes_feedback_stats and recipes_feedback_stats.avg_rating else 0.0
    
    return {
        "total_recipes_created": total_recipes_created,
        "total_recipes_saved": total_recipes_saved,
        "total_cooking_sessions": total_sessions,
        "completed_cooking_sessions": completed_sessions,
        "total_cooking_minutes": int(total_minutes),
        "total_feedbacks_given": total_feedbacks_given,
        "average_rating_given": round(float(avg_rating_given), 2),
        "recipes_received_feedbacks": recipes_received_feedbacks,
        "average_rating_received": round(avg_rating_received, 2)
    }


def update_user_profile(
    db: Session,
    user_id: int,
    *,
    name: Optional[str] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
    profile_url: Optional[str] = None
) -> User:
    """Update user profile information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    
    # Check if email is already taken by another user
    if email and email != user.email:
        existing_email = db.query(User).filter(
            User.email == email,
            User.id != user_id
        ).first()
        if existing_email:
            raise BadRequestException("Email already in use")
    
    # Check if username is already taken by another user
    if username and username != user.username:
        existing_username = db.query(User).filter(
            User.username == username,
            User.id != user_id
        ).first()
        if existing_username:
            raise BadRequestException("Username already in use")
    
    # Update fields
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email
    if username is not None:
        user.username = username
    if profile_url is not None:
        user.profile_url = profile_url
    
    db.commit()
    db.refresh(user)
    return user


def change_password(
    db: Session,
    user_id: int,
    *,
    current_password: str,
    new_password: str
) -> None:
    """Change user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    
    # Verify current password
    if not verify_password(current_password, user.password):
        raise UnauthorizedException("Current password is incorrect")
    
    # Validate new password
    if len(new_password) < 6:
        raise BadRequestException("New password must be at least 6 characters long")
    
    if current_password == new_password:
        raise BadRequestException("New password must be different from current password")
    
    # Update password
    user.password = get_password_hash(new_password)
    db.commit()


def delete_user_account(db: Session, user_id: int, *, password: str) -> None:
    """Delete user account (requires password confirmation)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    
    # Verify password
    if not verify_password(password, user.password):
        raise UnauthorizedException("Password is incorrect")
    
    # Delete user (cascade will handle related records)
    db.delete(user)
    db.commit()
