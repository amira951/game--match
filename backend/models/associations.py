from sqlalchemy import Table, Column, Integer, String, ForeignKey
from database import Base

has_liked_genre = Table(
    'has_liked_genre',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('item_name', String(100), nullable=False),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), nullable=False)
)

has_liked_tags = Table(
    'has_liked_tags',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('item_name', String(100), nullable=False),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), nullable=False)
)
