from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Базовая схема пользователя с общими атрибутами для всех схем
    пользователя"""

    username: str
    name: str
    surname: str
    email: EmailStr


class UserCreate(UserBase):
    """Схема, используемая при создании пользователя"""

    password: str


class User(UserBase):
    """Схема, используемая при возврате данных о пользователе из БД."""

    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Схема для возвращения пользователю данных о выпущенном токене."""
    access_token: str
    token_type: str


class PostBase(BaseModel):
    """Базовая схема для записей о зарплате и дате её повышения
    с общими атрибутами для всех схем зарплаты."""

    text: str


class PostCreate(PostBase):
    """Схема, используемая при создании поста."""
    author_id: int
    update_timestamp: int | None = None


class PostUpdate(PostBase):
    """Схема, используемая при изменении поста."""
    id: int
    update_timestamp: int


class PostLikeUpdate(BaseModel):
    """Схема, используемая для обновления кол-ва лайков у поста."""
    id: int
    like_count: int


class Post(PostCreate):
    """Схема для получения всех данных поста."""
    id: int
    create_timestamp: int
    like_count: int = 0

    class Config:
        from_attributes = True


class LikeBase(BaseModel):
    """Схема для создания и получения информации о лайках."""

    post_id: int
    liker_id: int

    class Config:
        from_attributes = True


class NotFound(BaseModel):
    """Схема для сообщения об остутсвии данных в БД."""

    detail: str = 'Запрошенные данные не найдены.'


class ForbiddenAction(BaseModel):
    """Схема для сообщения о не разрешенных действиях."""

    detail: str = 'Действие не разрешено'
