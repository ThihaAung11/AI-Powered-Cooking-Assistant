from fastapi import APIRouter, Query, status

from ..schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackOut
from ..utils.pagination import PaginationParams, PaginatedResponse
from ..services.feedback_service import (
    create_feedback,
    get_feedback,
    get_user_feedback_for_recipe,
    list_recipe_feedbacks,
    list_user_feedbacks,
    update_feedback,
    delete_feedback,
    get_recipe_rating_stats
)
from ..deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create(payload: FeedbackCreate, db: SessionDep, current_user: CurrentUser):
    """Create feedback for a recipe"""
    return create_feedback(
        db,
        recipe_id=payload.recipe_id,
        rating=payload.rating,
        comment=payload.comment,
        user_id=current_user.id
    )


@router.get("/my-feedbacks", response_model=PaginatedResponse[FeedbackOut])
def list_my_feedbacks(
    db: SessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """List all feedbacks by the current user"""
    params = PaginationParams(page=page, page_size=page_size)
    return list_user_feedbacks(db, current_user.id, params)


@router.get("/recipe/{recipe_id}", response_model=PaginatedResponse[FeedbackOut])
def list_recipe_feedback(
    recipe_id: int,
    db: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """List all feedbacks for a specific recipe"""
    params = PaginationParams(page=page, page_size=page_size)
    return list_recipe_feedbacks(db, recipe_id, params)


@router.get("/recipe/{recipe_id}/stats")
def get_recipe_stats(recipe_id: int, db: SessionDep):
    """Get rating statistics for a recipe"""
    return get_recipe_rating_stats(db, recipe_id)


@router.get("/recipe/{recipe_id}/my-feedback", response_model=FeedbackOut)
def get_my_feedback_for_recipe(
    recipe_id: int,
    db: SessionDep,
    current_user: CurrentUser
):
    """Get current user's feedback for a specific recipe"""
    from ..exceptions import NotFoundException
    
    feedback = get_user_feedback_for_recipe(db, current_user.id, recipe_id)
    if not feedback:
        raise NotFoundException("You haven't provided feedback for this recipe yet")
    return feedback


@router.get("/{feedback_id}", response_model=FeedbackOut)
def get_one(feedback_id: int, db: SessionDep):
    """Get a specific feedback by ID"""
    return get_feedback(db, feedback_id)


@router.put("/{feedback_id}", response_model=FeedbackOut)
def update(
    feedback_id: int,
    payload: FeedbackUpdate,
    db: SessionDep,
    current_user: CurrentUser
):
    """Update user's own feedback"""
    return update_feedback(
        db,
        feedback_id,
        user_id=current_user.id,
        rating=payload.rating,
        comment=payload.comment
    )


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(feedback_id: int, db: SessionDep, current_user: CurrentUser):
    """Delete user's own feedback"""
    delete_feedback(db, feedback_id, user_id=current_user.id)
    return None
