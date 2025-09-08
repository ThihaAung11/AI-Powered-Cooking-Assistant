from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=False)
    steps = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    creator = relationship("User", back_populates="recipes")
