"""
User Preference Service
Manage user cooking preferences
"""
from sqlalchemy.orm import Session
from typing import Optional

from ..models.user import User, UserPreference, SpiceLevel, Language
from ..exceptions import NotFoundException, BadRequestException


def get_user_preference(db: Session, user_id: int) -> Optional[UserPreference]:
    """Get user's preferences"""
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()


def create_user_preference(
    db: Session,
    *,
    user_id: int,
    language: Language = Language.english,
    spice_level: Optional[SpiceLevel] = None,
    diet_type: Optional[str] = None,
    allergies: Optional[str] = None,
    preferred_cuisine: Optional[str] = None,
    cooking_skill: Optional[str] = None
) -> UserPreference:
    """Create user preferences"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    
    # Check if preferences already exist
    existing = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if existing:
        raise BadRequestException("User preferences already exist. Use update instead.")
    
    preference = UserPreference(
        user_id=user_id,
        language=language,
        spice_level=spice_level,
        diet_type=diet_type,
        allergies=allergies,
        preferred_cuisine=preferred_cuisine,
        cooking_skill=cooking_skill
    )
    
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


def update_user_preference(
    db: Session,
    user_id: int,
    **updates
) -> UserPreference:
    """Update user preferences"""
    preference = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    
    if not preference:
        raise NotFoundException("User preferences not found. Create preferences first.")
    
    # Update only provided fields
    for key, value in updates.items():
        if value is not None and hasattr(preference, key):
            setattr(preference, key, value)
    
    db.commit()
    db.refresh(preference)
    return preference


def delete_user_preference(db: Session, user_id: int) -> None:
    """Delete user preferences (reset to defaults)"""
    preference = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    
    if not preference:
        raise NotFoundException("User preferences not found")
    
    db.delete(preference)
    db.commit()


def get_or_create_user_preference(db: Session, user_id: int) -> UserPreference:
    """Get user preferences or create with defaults if not exists"""
    preference = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    
    if not preference:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
        
        # Create with defaults
        preference = UserPreference(
            user_id=user_id,
            language=Language.english
        )
        db.add(preference)
        db.commit()
        db.refresh(preference)
    
    return preference
