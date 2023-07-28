"""Роутеры для едпойнтов юзера."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from business_layer import schemas
from business_layer.auth.hash_password import HashPassword
from business_layer.auth.jwt_handler import create_access_token
from db_layer import db_engine as db
from db_layer.crud import user_crud

router = APIRouter()
hash_password = HashPassword()


@router.get(
    path='/',
    summary='Посмотреть всех пользователей',
    response_model=list[schemas.User],
)
async def get_all_users(
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)]
) -> list[schemas.User]:
    return await user_crud.get_all(session=session)


@router.post(
    path='/signup',
    summary='Создание пользователя',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.User,
    responses={403: {'model': schemas.ForbiddenAction}}
)
async def create_user(
    new_user: schemas.UserCreate,
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
) -> schemas.User:
    hashed_password = hash_password.create_hash(new_user.password)
    new_user.password = hashed_password
    try:
        return await user_crud.create(
            new_obj=new_user,
            session=session)
    except IntegrityError as e:
        if 'UNIQUE constraint' in e.args[0]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Пользователь с таким username уже существует.')
        raise


@router.post(
    path='/login',
    summary='Вход в приложение',
    response_model=schemas.TokenResponse,
    responses={
        404: {'model': schemas.NotFound},
        403: {'model': schemas.ForbiddenAction},
        401: {'model': schemas.ForbiddenAction}},
)
async def sign_user_in(
    session: Annotated[db.AsyncSession, Depends(db.get_async_session)],
    user: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    user_exists = await user_crud.get_by_field(
        required_field='username',
        value=user.username,
        session=session)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден.')
    if not user_exists.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Пользователь неактивен.')
    if not hash_password.verify_hash(user.password, user_exists.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Введен неверный пароль.')
    access_token = create_access_token(user_exists.id)
    return {
        'access_token': access_token,
        'token_type': 'Bearer'
    }
