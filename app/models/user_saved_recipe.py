from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class UserSavedRecipe(CommonModel):
    __tablename__ = "user_saved_recipes"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_saved_user_recipe"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="saved_recipes")
    recipe: Mapped["Recipe"] = relationship(back_populates="saved_by")
