from typing import Any, Generic, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, func, select

from business_layer import schemas
from db_layer import db_engine
from db_layer.models import Like, Post, User

ModelType = TypeVar('ModelType', bound=db_engine.Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=schemas.BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=schemas.BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс с операциями CRUD."""

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: db_engine.AsyncSession
    ) -> ModelType | None:
        """Метод получает объект из БД по `id`."""
        return await session.get(self.model, obj_id)

    async def get_all(
        self,
        session: db_engine.AsyncSession
    ) -> list[ModelType]:
        """Метод получает все объекты из запрошенной таблицы."""
        objects = await session.scalars(select(self.model))
        return objects.all()

    async def get_by_field(
        self,
        required_field: str,
        value: Any,
        session: db_engine.AsyncSession,
        one_obj: bool = True
    ) -> ModelType | list[ModelType]:
        """Метод находит объекты по значению указанного поля."""
        field = getattr(self.model, required_field, None)
        if field is None:
            raise AttributeError(
                f'Поле {required_field} отсуствует в таблице'
            )
        query = select(self.model).where(field == value)
        if one_obj:
            return await session.scalar(query.limit(1))
        some_objs = await session.scalars(query)
        return some_objs.all()

    async def create(
        self,
        new_obj: CreateSchemaType,
        session: db_engine.AsyncSession,
    ) -> ModelType:
        """Метод создаёт запись в БД."""
        new_obj = new_obj.dict()
        new_obj = self.model(**new_obj)
        session.add(new_obj)
        await session.commit()
        await session.refresh(new_obj)
        return new_obj

    async def update(
        self,
        obj: ModelType,
        session: db_engine.AsyncSession,
        update_data: UpdateSchemaType,
    ) -> ModelType:
        """Метод обновляет запись указанного объекта в БД."""
        obj_data = jsonable_encoder(obj)
        update_data = update_data.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(obj, field, update_data[field])
        await session.commit()
        await session.refresh(obj)
        return obj

    async def remove(
        self,
        obj_id: int,
        session: db_engine.AsyncSession
    ) -> None:
        """Метод удаляет запись из БД."""
        stmt = delete(self.model).where(self.model.id == obj_id)
        await session.execute(stmt)
        await session.commit()


class CRUDUser(CRUDBase):
    """Класс с запросами к таблице `user`."""
    pass


class CRUDPost(CRUDBase):
    """Класс с запросами к таблице `salary`."""
    pass


class CRUDLike(CRUDBase):
    """Класс с запросами к таблице `salary`."""

    async def count_likes(self, post_id, session):
        """Метод для подсчета кол-ва лайков у поста."""
        query = (
            select(func.count("*"))
            .select_from(self.model)
            .where(self.model.post_id == post_id))
        return await session.scalar(query.limit(1))

    async def get_like(self, post_id, liker_id, session):
        """Метод для получения лайка по связке 'id поста - id пользователя,
        сделавшего лайк'."""
        query = (
            select(self.model)
            .where(self.model.post_id == post_id)
            .where(self.model.liker_id == liker_id))
        return await session.scalar(query.limit(1))


user_crud = CRUDUser(User)
post_crud = CRUDPost(Post)
like_crud = CRUDLike(Like)
