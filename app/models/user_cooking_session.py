from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class UserCookingSession(CommonModel):
    __tablename__ = "user_cooking_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    recipe_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recipes.id", ondelete="SET NULL"))
    started_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    ended_at: Mapped[Optional[datetime]] = mapped_column()
    duration_minutes: Mapped[Optional[int]] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="cooking_sessions")
    recipe: Mapped[Optional["Recipe"]] = relationship(back_populates="sessions")
