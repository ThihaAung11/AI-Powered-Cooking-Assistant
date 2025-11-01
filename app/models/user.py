from typing import Optional
from enum import StrEnum
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class SpiceLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class Language(StrEnum):
    english = "en"
    burmese = "my"


class User(CommonModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"))

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="users")
    preferences: Mapped[Optional["UserPreference"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    recipes: Mapped[list["Recipe"]] = relationship(back_populates="creator", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feedbacks: Mapped[list["UserFeedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    saved_recipes: Mapped[list["UserSavedRecipe"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    cooking_sessions: Mapped[list["UserCookingSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserPreference(CommonModel):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    language: Mapped[Language] = mapped_column(Enum(Language, name="language_enum"), default=Language.english)
    spice_level: Mapped[Optional[SpiceLevel]] = mapped_column(Enum(SpiceLevel, name="spice_level_enum"))
    diet_type: Mapped[Optional[str]] = mapped_column()
    allergies: Mapped[Optional[str]] = mapped_column()
    preferred_cuisine: Mapped[Optional[str]] = mapped_column()
    cooking_skill: Mapped[Optional[str]] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="preferences")


