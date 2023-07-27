"""Роутеры для едпойнтов лайков."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from business_layer import schemas, utilities
from business_layer.auth.authenticate import authenticate
from db_layer import db_engine as db
from db_layer.crud import like_crud, post_crud

router = APIRouter()


@router.post(
    path='/{post_id}',
    summary='Поставить лайк',
    responses={
        403: {'model': schemas.ForbiddenAction},
        404: {'model': schemas.NotFound}},
)
async def like_post(
    post_id: int,
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
    user: Annotated[schemas.User, Depends(authenticate)],
) -> schemas.LikeBase:
    post = await post_crud.get(obj_id=post_id, session=session)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пост не найден.')
    if post.author_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Лайк самому себе не разрешен.')
    like_schema = schemas.LikeBase(post_id=post_id, liker_id=user.id)
    try:
        obj = await like_crud.create(new_obj=like_schema, session=session)
        like = schemas.LikeBase.model_validate(obj)
        await utilities.change_like_in_post(post_id, session)
        return like

    except IntegrityError as e:
        if 'UNIQUE constraint' in e.args[0]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Повторный лайк не разрешен.')
        raise


@router.delete(
    path='/{post_id}',
    summary='Удалить лайк',
    status_code=status.HTTP_404_NOT_FOUND,
)
async def unlike_post(
    post_id: int,
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
    user: Annotated[schemas.User, Depends(authenticate)],
) -> schemas.NotFound:
    like_obj = await like_crud.get_like(
        post_id=int(post_id),
        liker_id=user.id,
        session=session,)
    if like_obj:
        await like_crud.remove(
            obj_id=like_obj.id,
            session=session,)
        await utilities.change_like_in_post(post_id, session)
    return {}
