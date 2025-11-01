from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import CommonModel


class Message(CommonModel):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user_message: Mapped[str] = mapped_column()
    ai_reply: Mapped[str] = mapped_column()
    user: Mapped["User"] = relationship(back_populates="messages")