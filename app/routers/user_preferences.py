from fastapi import APIRouter, status

from ..schemas.user_preference import (
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceOut
)
from ..services.user_preference_service import (
    get_user_preference,
    create_user_preference,
    update_user_preference,
    delete_user_preference,
    get_or_create_user_preference
)
from ..deps import CurrentUser, SessionDep
from ..exceptions import NotFoundException

router = APIRouter()


@router.get("/me", response_model=UserPreferenceOut)
def get_my_preferences(db: SessionDep, current_user: CurrentUser):
    """
    Get current user's preferences.
    Creates default preferences if they don't exist.
    """
    return get_or_create_user_preference(db, current_user.id)


@router.post("/", response_model=UserPreferenceOut, status_code=status.HTTP_201_CREATED)
def create_preferences(
    payload: UserPreferenceCreate,
    db: SessionDep,
    current_user: CurrentUser
):
    """
    Create user preferences.
    
    Note: Each user can only have one set of preferences.
    Use PUT to update existing preferences.
    """
    return create_user_preference(
        db,
        user_id=current_user.id,
        language=payload.language,
        spice_level=payload.spice_level,
        diet_type=payload.diet_type,
        allergies=payload.allergies,
        preferred_cuisine=payload.preferred_cuisine,
        cooking_skill=payload.cooking_skill
    )


@router.put("/", response_model=UserPreferenceOut)
def update_preferences(
    payload: UserPreferenceUpdate,
    db: SessionDep,
    current_user: CurrentUser
):
    """
    Update user preferences.
    
    Only provided fields will be updated.
    Omitted fields will remain unchanged.
    """
    return update_user_preference(
        db,
        current_user.id,
        language=payload.language,
        spice_level=payload.spice_level,
        diet_type=payload.diet_type,
        allergies=payload.allergies,
        preferred_cuisine=payload.preferred_cuisine,
        cooking_skill=payload.cooking_skill
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_preferences(db: SessionDep, current_user: CurrentUser):
    """
    Delete user preferences (reset to defaults).
    
    This will remove all custom preferences.
    The system will use default values for recommendations.
    """
    delete_user_preference(db, current_user.id)
    return None


@router.get("/options")
def get_preference_options():
    """
    Get available options for user preferences.
    
    Returns valid values for enums and recommended values for other fields.
    """
    return {
        "language": {
            "type": "enum",
            "values": ["en", "my"],
            "labels": {
                "en": "English",
                "my": "Burmese (Myanmar)"
            }
        },
        "spice_level": {
            "type": "enum",
            "values": ["low", "medium", "high"],
            "labels": {
                "low": "Low (Mild)",
                "medium": "Medium",
                "high": "High (Spicy)"
            }
        },
        "diet_type": {
            "type": "string",
            "examples": [
                "omnivore",
                "vegetarian",
                "vegan",
                "pescatarian",
                "halal",
                "kosher"
            ]
        },
        "cooking_skill": {
            "type": "string",
            "examples": [
                "beginner",
                "intermediate",
                "advanced",
                "expert"
            ]
        },
        "preferred_cuisine": {
            "type": "string",
            "examples": [
                "Burmese",
                "Thai",
                "Chinese",
                "Indian",
                "Italian",
                "Japanese",
                "Korean",
                "Vietnamese",
                "Mexican",
                "Mediterranean"
            ]
        },
        "allergies": {
            "type": "string",
            "description": "Comma-separated list of allergies",
            "examples": [
                "peanuts, tree nuts",
                "shellfish",
                "dairy",
                "gluten",
                "soy"
            ]
        }
    }
