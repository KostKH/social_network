from datetime import datetime

from fastapi import HTTPException, status
from jose import JWTError, jwt

from config import Settings

settings = Settings()


def create_access_token(user_id: int) -> str:
    """Функция для создания токена на основе user_id и секрета, заданного
    в настройках. Токен действителен в течение указанного в настройках
    кол-ва секунд."""
    payload = {
        'user_id': user_id,
        'expires': datetime.now().timestamp() + settings.jwt_effect_seconds
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def verify_access_token(token: str) -> dict:
    """Функция проверяет на валидность переданный в неё токен.
    В случае успешной валидации функция возвращает расшифрованный
    словарь, содержащий user_id и дату окончания срока действия."""
    try:
        data = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    expire = data.get('expires')

    if expire is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token supplied"
        )
    if datetime.now() > datetime.fromtimestamp(expire):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token expired!"
        )
    return data
