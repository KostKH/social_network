"""Роутеры для едпойнтов поста."""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from business_layer import schemas
from business_layer.auth.authenticate import authenticate
from db_layer import db_engine as db
from db_layer.crud import post_crud

router = APIRouter()


@router.get(
    path='/',
    summary='Показать список постов',
    response_model=list[schemas.Post],)
async def get_all_posts(
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
) -> list[schemas.Post]:
    return await post_crud.get_all(session=session)


@router.post(
    path='/',
    summary='Разместить пост',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,)
async def create_post(
    new_post: schemas.PostBase,
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
    user: Annotated[schemas.User, Depends(authenticate)],
) -> schemas.Post:
    enriched_post = schemas.PostCreate(
        text=new_post.text,
        author_id=user.id,
    )
    return await post_crud.create(
        new_obj=enriched_post,
        session=session)


@router.get(
    path='/{post_id}',
    summary='Показать пост',
    response_model=schemas.Post,
    responses={404: {'model': schemas.NotFound}},)
async def get_post(
    post_id: int,
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
) -> schemas.Post:
    post = await post_crud.get(obj_id=post_id, session=session)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пост не найден.')
    return post


@router.patch(
    path='/{post_id}',
    summary='Изменить пост',
    response_model=schemas.Post,
    responses={
        404: {'model': schemas.NotFound},
        403: {'model': schemas.ForbiddenAction}},
)
async def update_post(
    post_id: int,
    input_data: schemas.PostBase,
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
    user: Annotated[schemas.User, Depends(authenticate)],
) -> schemas.Post:
    post_to_update = await post_crud.get(obj_id=post_id, session=session)
    if not post_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пост не найден.')
    if post_to_update.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Редактировать можно только свои посты.')
    updated_data = schemas.PostUpdate(
        id=post_id,
        text=input_data.text,
        update_timestamp=int(datetime.utcnow().timestamp())
    )
    return await post_crud.update(
        obj=post_to_update,
        update_data=updated_data,
        session=session)


@router.delete(
    path='/{post_id}',
    summary='Удалить пост',
    status_code=status.HTTP_404_NOT_FOUND,
    responses={403: {'model': schemas.ForbiddenAction}},)
async def delete_post(
    post_id: int,
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
    user: Annotated[schemas.User, Depends(authenticate)],
) -> schemas.NotFound:
    post_to_delete = await post_crud.get(obj_id=post_id, session=session)
    if not post_to_delete:
        return {}
    if post_to_delete.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Удалять можно только свои посты.')
    await post_crud.remove(
        obj_id=post_to_delete.id,
        session=session,)
    return {}
