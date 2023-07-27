from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import mapped_column, relationship

from .db_engine import Base


class User(Base):
    """Модель Алхимии к таблице user в БД."""
    username = mapped_column(String, nullable=False, unique=True)
    password = mapped_column(String, nullable=False)
    name = mapped_column(String, nullable=False)
    surname = mapped_column(String, nullable=False)
    email = mapped_column(String, nullable=False)
    is_active = mapped_column(Boolean, default=True)
    is_superuser = mapped_column(Boolean, default=False)
    posts = relationship('Post', back_populates='author')
    liked_posts = relationship("Like", back_populates='liker')


class Post(Base):
    """Модель Алхимии к таблице salary в БД."""

    text = mapped_column(String, nullable=False)
    author_id = mapped_column(
        Integer,
        ForeignKey('user.id'),
        nullable=False)
    create_timestamp = mapped_column(
        Integer,
        default=lambda: int(datetime.utcnow().timestamp()))
    update_timestamp = mapped_column(Integer, nullable=True)
    author = relationship("User", back_populates='posts')
    likers = relationship("Like", back_populates='post')
    like_count = mapped_column(Integer, default=0)


class Like(Base):
    """Модель Алхимии к таблице like в БД."""

    post_id = mapped_column(
        Integer,
        ForeignKey('post.id'),
        nullable=False,)
    liker_id = mapped_column(
        Integer,
        ForeignKey('user.id'),
        nullable=False,)
    liker = relationship(
        'User',
        back_populates='liked_posts',
        cascade='all, delete')
    post = relationship(
        'Post',
        back_populates='likers',
        cascade="all, delete")
    __table_args__ = (UniqueConstraint('post_id', 'liker_id'), )
