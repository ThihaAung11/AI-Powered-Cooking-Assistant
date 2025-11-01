from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from ..models.user import SpiceLevel, Language


class UserPreferenceBase(BaseModel):
    language: Optional[Language] = Field(Language.english, description="Preferred language")
    spice_level: Optional[SpiceLevel] = Field(None, description="Preferred spice level")
    diet_type: Optional[str] = Field(None, max_length=50, description="Diet type (vegetarian, vegan, etc.)")
    allergies: Optional[str] = Field(None, max_length=500, description="Food allergies or intolerances")
    preferred_cuisine: Optional[str] = Field(None, max_length=100, description="Preferred cuisine type")
    cooking_skill: Optional[str] = Field(None, max_length=50, description="Cooking skill level (beginner, intermediate, advanced)")


class UserPreferenceCreate(UserPreferenceBase):
    pass


class UserPreferenceUpdate(BaseModel):
    language: Optional[Language] = None
    spice_level: Optional[SpiceLevel] = None
    diet_type: Optional[str] = Field(None, max_length=50)
    allergies: Optional[str] = Field(None, max_length=500)
    preferred_cuisine: Optional[str] = Field(None, max_length=100)
    cooking_skill: Optional[str] = Field(None, max_length=50)


class UserPreferenceOut(UserPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
