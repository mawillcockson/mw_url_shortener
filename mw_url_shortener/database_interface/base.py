# mypy: allow_any_expr
from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as BaseSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener.database.models.base import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
ObjectSchemaType = TypeVar("ObjectSchemaType", bound=BaseSchema)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class InterfaceBase(
    Generic[ModelType, ObjectSchemaType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: Type[ModelType], schema: Type[ObjectSchemaType]):
        """
        interface object with default methods to create, read, update, delete
        """
        self.model = model
        self.schema = schema

    async def get_by_id(self, async_session: AsyncSession, id: int) -> ObjectSchemaType:
        async with async_session.begin():
            object_model = (
                await async_session.execute(select(self.model).where(self.model.id == id))
            ).scalar_one()
            assert isinstance(
                object_model, self.model
            ), f"expected '{self.model}', got '{type(object_model)}'"
            return self.schema.from_orm(object_model)

    async def get_multiple(
        self, async_session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ObjectSchemaType]:
        objects: List[ObjectSchemaType] = []
        async with async_session.begin():
            query = select(self.model).offset(skip).limit(limit)
            object_models = (await async_session.execute(query)).scalars().all()
            for object_model in object_models:
                objects.append(self.schema.from_orm(object_model))
        return objects

    async def create(
        self, async_session: AsyncSession, *, object_schema_in: CreateSchemaType
    ) -> ObjectSchemaType:
        object_in_data = jsonable_encoder(object_schema_in)
        object_model = self.model(**object_in_data)
        async with async_session.begin():
            async_session.add(object_model)
        await async_session.refresh(object_model)
        await async_session.close()  # .refresh() opens a new session
        return self.schema.from_orm(object_model)

    async def update(
        self,
        async_session: AsyncSession,
        *,
        current_object_model: ModelType,
        object_update_schema: UpdateSchemaType,
    ) -> ObjectSchemaType:
        current_data = jsonable_encoder(current_object_model)
        update_data = object_update_schema.dict(exclude_unset=True)
        for field in current_data:
            if field in update_data:
                setattr(current_object_model, field, update_data[field])

        async with async_session.begin():
            async_session.add(current_object_model)
            return self.schema.from_orm(current_object_model)

    async def remove_by_id(
        self, async_session: AsyncSession, *, id: int
    ) -> ObjectSchemaType:
        async with async_session.begin():
            get_by_id = select(self.model).where(self.model.id == id)
            object_model = (await async_session.execute(get_by_id)).scalar_one()
            await async_session.delete(object_model)
            object_schema = self.schema.from_orm(object_model)
            object_schema_with_id = object_schema.update({"id": id})
            return object_schema_with_id
