from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import func, desc

from ..models.user_cooking_session import UserCookingSession
from ..models.recipe import Recipe
from ..schemas.cooking_session import CookingSessionOut, CookingSessionStats
from ..utils.pagination import PaginationParams, PaginatedResponse, paginate
from ..exceptions import NotFoundException, BadRequestException, UnauthorizedException


def start_cooking_session(
    db: Session,
    *,
    recipe_id: Optional[int],
    user_id: int
) -> UserCookingSession:
    """Start a new cooking session"""
    # Verify recipe exists if provided
    if recipe_id:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise NotFoundException("Recipe not found")
    
    # Check if user has an active session
    active_session = db.query(UserCookingSession).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.ended_at.is_(None)
    ).first()
    
    if active_session:
        raise BadRequestException("You already have an active cooking session. End it before starting a new one.")
    
    session = UserCookingSession(
        user_id=user_id,
        recipe_id=recipe_id,
        started_at=datetime.now(timezone.utc)
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def end_cooking_session(
    db: Session,
    session_id: int,
    *,
    user_id: int
) -> UserCookingSession:
    """End an active cooking session"""
    session = db.query(UserCookingSession).filter(UserCookingSession.id == session_id).first()
    
    if not session:
        raise NotFoundException("Cooking session not found")
    
    if session.user_id != user_id:
        raise UnauthorizedException("You are not allowed to modify this session")
    
    if session.ended_at is not None:
        raise BadRequestException("This session has already ended")
    
    now = datetime.now(timezone.utc)
    session.ended_at = now
    
    # Calculate duration in minutes
    duration = (now - session.started_at).total_seconds() / 60
    session.duration_minutes = int(duration)
    
    db.commit()
    db.refresh(session)
    return session


def get_cooking_session(db: Session, session_id: int) -> UserCookingSession:
    """Get a specific cooking session by ID"""
    session = db.query(UserCookingSession).filter(UserCookingSession.id == session_id).first()
    if not session:
        raise NotFoundException("Cooking session not found")
    return session


def get_active_session(db: Session, user_id: int) -> Optional[UserCookingSession]:
    """Get user's active cooking session if any"""
    return db.query(UserCookingSession).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.ended_at.is_(None)
    ).first()


def list_user_sessions(
    db: Session,
    user_id: int,
    params: Optional[PaginationParams] = None,
    active_only: bool = False
) -> PaginatedResponse[CookingSessionOut]:
    """List user's cooking sessions with pagination"""
    query = db.query(UserCookingSession).filter(
        UserCookingSession.user_id == user_id
    )
    
    if active_only:
        query = query.filter(UserCookingSession.ended_at.is_(None))
    
    query = query.order_by(desc(UserCookingSession.started_at))
    
    if params is None:
        params = PaginationParams()
    
    return paginate(query, params, CookingSessionOut)


def list_recipe_sessions(
    db: Session,
    recipe_id: int,
    params: Optional[PaginationParams] = None
) -> PaginatedResponse[CookingSessionOut]:
    """List all cooking sessions for a specific recipe"""
    # Verify recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise NotFoundException("Recipe not found")
    
    query = db.query(UserCookingSession).filter(
        UserCookingSession.recipe_id == recipe_id
    ).order_by(desc(UserCookingSession.started_at))
    
    if params is None:
        params = PaginationParams()
    
    return paginate(query, params, CookingSessionOut)


def delete_cooking_session(db: Session, session_id: int, *, user_id: int) -> None:
    """Delete a cooking session"""
    session = get_cooking_session(db, session_id)
    
    if session.user_id != user_id:
        raise UnauthorizedException("You are not allowed to delete this session")
    
    db.delete(session)
    db.commit()


def get_user_cooking_stats(db: Session, user_id: int) -> CookingSessionStats:
    """Get cooking statistics for a user"""
    # Total sessions
    total_sessions = db.query(func.count(UserCookingSession.id)).filter(
        UserCookingSession.user_id == user_id
    ).scalar() or 0
    
    # Completed sessions
    completed_sessions = db.query(func.count(UserCookingSession.id)).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.ended_at.isnot(None)
    ).scalar() or 0
    
    # Active sessions
    active_sessions = total_sessions - completed_sessions
    
    # Total cooking time
    total_minutes = db.query(func.sum(UserCookingSession.duration_minutes)).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.duration_minutes.isnot(None)
    ).scalar() or 0
    
    # Average session duration
    avg_minutes = db.query(func.avg(UserCookingSession.duration_minutes)).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.duration_minutes.isnot(None)
    ).scalar() or 0.0
    
    # Most cooked recipe
    most_cooked = db.query(
        UserCookingSession.recipe_id,
        func.count(UserCookingSession.id).label('count')
    ).filter(
        UserCookingSession.user_id == user_id,
        UserCookingSession.recipe_id.isnot(None)
    ).group_by(UserCookingSession.recipe_id).order_by(desc('count')).first()
    
    most_cooked_recipe_id = None
    most_cooked_recipe_title = None
    
    if most_cooked:
        most_cooked_recipe_id = most_cooked.recipe_id
        recipe = db.query(Recipe).filter(Recipe.id == most_cooked_recipe_id).first()
        if recipe:
            most_cooked_recipe_title = recipe.title
    
    return CookingSessionStats(
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        active_sessions=active_sessions,
        total_cooking_minutes=int(total_minutes),
        average_session_minutes=round(float(avg_minutes), 2),
        most_cooked_recipe_id=most_cooked_recipe_id,
        most_cooked_recipe_title=most_cooked_recipe_title
    )
