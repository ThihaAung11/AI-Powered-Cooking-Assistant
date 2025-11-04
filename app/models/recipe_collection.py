from typing import Optional
from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class RecipeCollection(CommonModel):
    """User's recipe collections for organizing recipes into meal plans or custom groups"""
    __tablename__ = "recipe_collections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column()  # "Weekly Meal Plan", "Quick Dinners"
    description: Mapped[Optional[str]] = mapped_column()
    collection_type: Mapped[str] = mapped_column(default="custom")  # "meal_plan", "favorites", "custom"
    is_public: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="collections")
    items: Mapped[list["CollectionItem"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan",
        order_by="CollectionItem.order"
    )


class CollectionItem(CommonModel):
    """Individual recipe items within a collection with ordering and meal planning metadata"""
    __tablename__ = "collection_items"
    __table_args__ = (
        UniqueConstraint("collection_id", "recipe_id", name="uq_collection_recipe"),
        Index("ix_collection_items_collection", "collection_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("recipe_collections.id", ondelete="CASCADE"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(default=0)  # Display order
    
    # Meal planning specific fields
    day_of_week: Mapped[Optional[str]] = mapped_column()  # "Monday", "Tuesday", etc.
    meal_type: Mapped[Optional[str]] = mapped_column()  # "breakfast", "lunch", "dinner", "snack"
    notes: Mapped[Optional[str]] = mapped_column()  # "Prep night before", "Double batch"
    servings: Mapped[Optional[int]] = mapped_column()  # Override recipe default servings
    
    # Relationships
    collection: Mapped["RecipeCollection"] = relationship(back_populates="items")
    recipe: Mapped["Recipe"] = relationship()
