from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func

from ..models.user_feedback import UserFeedback
from ..models.recipe import Recipe
from ..schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackOut
from ..utils.pagination import PaginationParams, PaginatedResponse, paginate
from ..exceptions import NotFoundException, UnauthorizedException, BadRequestException


def create_feedback(
    db: Session,
    *,
    recipe_id: int,
    rating: int,
    comment: Optional[str],
    user_id: int
) -> UserFeedback:
    """Create feedback for a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise NotFoundException("Recipe not found")
    
    # Check if user already gave feedback for this recipe
    existing = db.query(UserFeedback).filter(
        UserFeedback.user_id == user_id,
        UserFeedback.recipe_id == recipe_id
    ).first()
    
    if existing:
        raise BadRequestException("You have already provided feedback for this recipe. Use update instead.")
    
    feedback = UserFeedback(
        user_id=user_id,
        recipe_id=recipe_id,
        rating=rating,
        comment=comment
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback(db: Session, feedback_id: int) -> UserFeedback:
    """Get a specific feedback by ID"""
    feedback = db.query(UserFeedback).filter(UserFeedback.id == feedback_id).first()
    if not feedback:
        raise NotFoundException("Feedback not found")
    return feedback


def get_user_feedback_for_recipe(db: Session, user_id: int, recipe_id: int) -> Optional[UserFeedback]:
    """Get user's feedback for a specific recipe"""
    return db.query(UserFeedback).filter(
        UserFeedback.user_id == user_id,
        UserFeedback.recipe_id == recipe_id
    ).first()


def list_recipe_feedbacks(
    db: Session,
    recipe_id: int,
    params: Optional[PaginationParams] = None
) -> PaginatedResponse[FeedbackOut]:
    """List all feedbacks for a recipe with pagination"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise NotFoundException("Recipe not found")
    
    query = db.query(UserFeedback).filter(
        UserFeedback.recipe_id == recipe_id
    ).order_by(UserFeedback.created_at.desc())
    
    if params is None:
        params = PaginationParams()
    
    return paginate(query, params, FeedbackOut)


def list_user_feedbacks(
    db: Session,
    user_id: int,
    params: Optional[PaginationParams] = None
) -> PaginatedResponse[FeedbackOut]:
    """List all feedbacks by a user with pagination"""
    query = db.query(UserFeedback).filter(
        UserFeedback.user_id == user_id
    ).order_by(UserFeedback.created_at.desc())
    
    if params is None:
        params = PaginationParams()
    
    return paginate(query, params, FeedbackOut)


def update_feedback(
    db: Session,
    feedback_id: int,
    *,
    user_id: int,
    rating: Optional[int] = None,
    comment: Optional[str] = None
) -> UserFeedback:
    """Update user's feedback"""
    feedback = get_feedback(db, feedback_id)
    
    # Check if user owns this feedback
    if feedback.user_id != user_id:
        raise UnauthorizedException("You are not allowed to modify this feedback")
    
    if rating is not None:
        feedback.rating = rating
    if comment is not None:
        feedback.comment = comment
    
    db.commit()
    db.refresh(feedback)
    return feedback


def delete_feedback(db: Session, feedback_id: int, *, user_id: int) -> None:
    """Delete user's feedback"""
    feedback = get_feedback(db, feedback_id)
    
    # Check if user owns this feedback
    if feedback.user_id != user_id:
        raise UnauthorizedException("You are not allowed to delete this feedback")
    
    db.delete(feedback)
    db.commit()


def get_recipe_rating_stats(db: Session, recipe_id: int) -> dict:
    """Get rating statistics for a recipe"""
    stats = db.query(
        func.count(UserFeedback.id).label('total_feedbacks'),
        func.avg(UserFeedback.rating).label('average_rating'),
        func.min(UserFeedback.rating).label('min_rating'),
        func.max(UserFeedback.rating).label('max_rating')
    ).filter(UserFeedback.recipe_id == recipe_id).first()
    
    return {
        "recipe_id": recipe_id,
        "total_feedbacks": stats.total_feedbacks or 0,
        "average_rating": round(float(stats.average_rating), 2) if stats.average_rating else 0.0,
        "min_rating": stats.min_rating or 0,
        "max_rating": stats.max_rating or 0
    }
