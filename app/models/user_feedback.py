from typing import Optional
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class UserFeedback(CommonModel):
    __tablename__ = "user_feedback"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_feedback_user_recipe"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_rating_between_1_5"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column()
    comment: Mapped[Optional[str]] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="feedbacks")
    recipe: Mapped["Recipe"] = relationship(back_populates="feedbacks")
