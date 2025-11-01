from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class Role(CommonModel):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column()

    users: Mapped[list["User"]] = relationship(back_populates="role")
