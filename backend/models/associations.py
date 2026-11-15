from sqlalchemy import Table, Column, Integer, String, ForeignKey
from database import Base

class HasLikedGenre(Base):
    __tablename__ = 'has_liked_genre'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(100), nullable=False) # Ex: le pseudo de l'utilisateur
    genre_id = Column(Integer, ForeignKey('genres.id', ondelete='CASCADE'), nullable=False)


class HasLikedTags(Base):
    __tablename__ = 'has_liked_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(100), nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), nullable=False)
