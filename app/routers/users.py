from fastapi import APIRouter, status

from ..schemas.user import UserProfile, UserUpdate, UserStats, PasswordChange
from ..services.user_profile_service import (
    get_user_profile,
    get_user_stats,
    update_user_profile,
    change_password,
    delete_user_account
)
from ..deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/me", response_model=UserProfile)
def get_my_profile(db: SessionDep, current_user: CurrentUser):
    """
    Get current user's profile with basic statistics.
    
    Includes:
    - User information (name, email, username)
    - Total recipes created
    - Total recipes saved
    - Total cooking sessions
    - Total feedbacks given
    """
    return get_user_profile(db, current_user.id)


@router.put("/me", response_model=UserProfile)
def update_my_profile(
    payload: UserUpdate,
    db: SessionDep,
    current_user: CurrentUser
):
    """
    Update current user's profile information.
    
    Updatable fields:
    - name
    - email (must be unique)
    - username (must be unique)
    
    Only provided fields will be updated.
    """
    update_user_profile(
        db,
        current_user.id,
        name=payload.name,
        email=payload.email,
        username=payload.username
    )
    return get_user_profile(db, current_user.id)


@router.get("/me/stats", response_model=UserStats)
def get_my_stats(db: SessionDep, current_user: CurrentUser):
    """
    Get detailed statistics about current user's activity.
    
    Includes:
    - Recipes created and saved
    - Cooking sessions (total and completed)
    - Total cooking time
    - Feedbacks given and received
    - Average ratings (given and received)
    """
    return get_user_stats(db, current_user.id)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_my_password(
    payload: PasswordChange,
    db: SessionDep,
    current_user: CurrentUser
):
    """
    Change current user's password.
    
    Requires:
    - Current password (for verification)
    - New password (min 6 characters, must be different)
    """
    change_password(
        db,
        current_user.id,
        current_password=payload.current_password,
        new_password=payload.new_password
    )
    return None


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    password: str,
    db: SessionDep,
    current_user: CurrentUser
):
    """
    Delete current user's account.
    
    ⚠️ WARNING: This action is irreversible!
    
    This will delete:
    - User account
    - All recipes created by user
    - All cooking sessions
    - All feedbacks
    - All saved recipes
    - User preferences
    
    Requires password confirmation for security.
    """
    delete_user_account(db, current_user.id, password=password)
    return None
