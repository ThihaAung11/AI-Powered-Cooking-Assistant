from typing import Optional
from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class Recipe(CommonModel):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    cuisine: Mapped[Optional[str]] = mapped_column()
    difficulty: Mapped[Optional[str]] = mapped_column()
    total_time: Mapped[Optional[int]] = mapped_column()  # minutes
    ingredients: Mapped[str] = mapped_column()
    image_url: Mapped[Optional[str]] = mapped_column()
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)

    # Relationships
    creator: Mapped["User"] = relationship(back_populates='recipes')
    steps: Mapped[list["CookingStep"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    feedbacks: Mapped[list["UserFeedback"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    saved_by: Mapped[list["UserSavedRecipe"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    sessions: Mapped[list["UserCookingSession"]] = relationship(back_populates="recipe")


class CookingStep(CommonModel):
    __tablename__ = "cooking_steps"
    __table_args__ = (
        UniqueConstraint("recipe_id", "step_number", name="uq_recipe_step"),
        Index("ix_cooking_steps_recipe", "recipe_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    step_number: Mapped[int] = mapped_column()
    instruction_text: Mapped[str] = mapped_column()
    media_url: Mapped[Optional[str]] = mapped_column()

    recipe: Mapped["Recipe"] = relationship(back_populates="steps")
