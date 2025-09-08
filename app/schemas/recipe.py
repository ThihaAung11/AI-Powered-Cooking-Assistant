from pydantic import BaseModel
from typing import Optional


class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    ingredients: str
    steps: str


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    steps: Optional[str] = None


class RecipeOut(RecipeBase):
    id: int
    created_by: int

    class Config:
        from_attributes = True
