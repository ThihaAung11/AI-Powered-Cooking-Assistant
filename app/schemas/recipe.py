from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CookingStepBase(BaseModel):
    step_number: int
    instruction_text: str
    media_url: Optional[str] = None


class CookingStepCreate(CookingStepBase):
    pass


class CookingStepOut(CookingStepBase):
    id: int
    recipe_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    total_time: Optional[int] = None  # minutes
    ingredients: str
    image_url: Optional[str] = None


class RecipeCreate(RecipeBase):
    steps: List[CookingStepCreate] = []


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    total_time: Optional[int] = None
    ingredients: Optional[str] = None
    image_url: Optional[str] = None
    steps: Optional[List[CookingStepCreate]] = None


class RecipeOut(RecipeBase):
    id: int
    created_by: int
    steps: List[CookingStepOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
