from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    liked_items = relationship("HasLikedGenre", back_populates="genre", cascade="all, delete-orphan")
