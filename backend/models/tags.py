from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)


    liked_items = relationship("HasLikedTags", back_populates="tag", cascade="all, delete-orphan")
