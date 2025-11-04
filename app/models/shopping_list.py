from typing import Optional
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class ShoppingList(CommonModel):
    """Shopping list generated from recipes or created manually"""
    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column()  # "Week of Nov 4", "Grocery Run"
    description: Mapped[Optional[str]] = mapped_column()
    is_completed: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="shopping_lists")
    items: Mapped[list["ShoppingListItem"]] = relationship(
        back_populates="shopping_list",
        cascade="all, delete-orphan",
        order_by="ShoppingListItem.category, ShoppingListItem.ingredient"
    )


class ShoppingListItem(CommonModel):
    """Individual item in a shopping list"""
    __tablename__ = "shopping_list_items"
    __table_args__ = (
        Index("ix_shopping_list_items_list", "shopping_list_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    shopping_list_id: Mapped[int] = mapped_column(ForeignKey("shopping_lists.id", ondelete="CASCADE"))
    ingredient: Mapped[str] = mapped_column()  # "Chicken breast"
    quantity: Mapped[Optional[str]] = mapped_column()  # "500g", "2 cups"
    category: Mapped[str] = mapped_column(default="Other")  # "Produce", "Dairy", "Meat", "Pantry"
    is_checked: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[Optional[str]] = mapped_column()
    
    # Track which recipe this came from (optional)
    source_recipe_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recipes.id", ondelete="SET NULL"))
    
    # Relationships
    shopping_list: Mapped["ShoppingList"] = relationship(back_populates="items")
    source_recipe: Mapped[Optional["Recipe"]] = relationship()
