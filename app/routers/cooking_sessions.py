from fastapi import APIRouter, Query, status

from ..schemas.cooking_session import (
    CookingSessionCreate,
    CookingSessionOut,
    CookingSessionEnd,
    CookingSessionStats
)
from ..utils.pagination import PaginationParams, PaginatedResponse
from ..services.cooking_session_service import (
    start_cooking_session,
    end_cooking_session,
    get_cooking_session,
    get_active_session,
    list_user_sessions,
    list_recipe_sessions,
    delete_cooking_session,
    get_user_cooking_stats
)
from ..deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=CookingSessionOut, status_code=status.HTTP_201_CREATED)
def start_session(payload: CookingSessionCreate, db: SessionDep, current_user: CurrentUser):
    """Start a new cooking session"""
    return start_cooking_session(
        db,
        recipe_id=payload.recipe_id,
        user_id=current_user.id
    )


@router.post("/{session_id}/end", response_model=CookingSessionOut)
def end_session(
    session_id: int,
    db: SessionDep,
    current_user: CurrentUser
):
    """End an active cooking session"""
    return end_cooking_session(db, session_id, user_id=current_user.id)


@router.get("/active", response_model=CookingSessionOut)
def get_active(db: SessionDep, current_user: CurrentUser):
    """Get current user's active cooking session"""
    from ..exceptions import NotFoundException
    
    session = get_active_session(db, current_user.id)
    if not session:
        raise NotFoundException("No active cooking session found")
    return session


@router.get("/my-sessions", response_model=PaginatedResponse[CookingSessionOut])
def list_my_sessions(
    db: SessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(False, description="Show only active sessions")
):
    """List current user's cooking sessions"""
    params = PaginationParams(page=page, page_size=page_size)
    return list_user_sessions(db, current_user.id, params, active_only=active_only)


@router.get("/my-stats", response_model=CookingSessionStats)
def get_my_stats(db: SessionDep, current_user: CurrentUser):
    """Get current user's cooking statistics"""
    return get_user_cooking_stats(db, current_user.id)


@router.get("/recipe/{recipe_id}", response_model=PaginatedResponse[CookingSessionOut])
def list_recipe_session(
    recipe_id: int,
    db: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """List all cooking sessions for a specific recipe"""
    params = PaginationParams(page=page, page_size=page_size)
    return list_recipe_sessions(db, recipe_id, params)


@router.get("/{session_id}", response_model=CookingSessionOut)
def get_one(session_id: int, db: SessionDep):
    """Get a specific cooking session by ID"""
    return get_cooking_session(db, session_id)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(session_id: int, db: SessionDep, current_user: CurrentUser):
    """Delete a cooking session"""
    delete_cooking_session(db, session_id, user_id=current_user.id)
    return None
