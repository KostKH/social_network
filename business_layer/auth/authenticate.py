from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from db_layer import db_engine as db
from db_layer import models
from db_layer.crud import user_crud

from .jwt_handler import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/signin')


async def authenticate(
    session: Annotated[db.AsyncSession,
                       Depends(db.get_async_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
) -> models.User:
    """Функция для обработки переданного на эндпойнт токена. Функция
    проверяет токен на валидность и срок действия, затем по user_id
    проверяет наличие пользователя в базе данных и его статус (пользователь
    должен быть активен, не отключен). Если проверки пройдены - функция
    возвращает объект пользователя из БД."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=('Для получения доступа авторизуйтейсь '
                    'и добавьте токен в запрос.'))
    decoded_token = verify_access_token(token)
    user = await user_crud.get(
        obj_id=decoded_token['user_id'],
        session=session)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=('Пользователь не найден.'))
    return user
