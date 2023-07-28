"""Подключение всех роутеров к главному роутеру."""
from fastapi import APIRouter

from . import like, posts, user

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(
    router=posts.router,
    prefix='/posts',
    tags=['Posts'],
)
main_router.include_router(
    router=user.router,
    prefix='/users',
    tags=['Users']
)
main_router.include_router(
    router=like.router,
    prefix='/like',
    tags=['Likes']
)
