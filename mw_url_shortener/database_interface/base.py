# mypy: allow_any_expr
from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as BaseSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener.database.models.base import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class InterfaceBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        interface object with default methods to create, read, update, delete
        """
        self.model = model

    async def get_by_id(self, async_session: AsyncSession, id: int) -> ModelType:
        object_model = (
            await async_session.execute(select(self.model).where(self.model.id == id))
        ).scalar_one()
        assert isinstance(
            object_model, self.model
        ), f"expected '{type(self.model)}', got '{type(object_model)}'"
        return object_model

    async def get_multiple(
        self, async_session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        async with async_session.begin():
            statement = select(self.model).offset(skip).limit(limit)
            object_models = (await async_session.execute(statement)).scalars().all()
        for object_model in object_models:
            await async_session.refresh(object_model)
        return object_models

    async def create(
        self, async_session: AsyncSession, *, object_schema_in: CreateSchemaType
    ) -> ModelType:
        object_in_data = jsonable_encoder(object_schema_in)
        object_model = self.model(**object_in_data)
        async with async_session.begin():
            async_session.add(object_model)
        await async_session.refresh(object_model)
        return object_model

    async def update(
        self,
        async_session: AsyncSession,
        *,
        current_object_model: ModelType,
        object_update_schema: UpdateSchemaType,
    ) -> ModelType:
        current_data = jsonable_encoder(current_object_model)
        update_data = object_update_schema.dict(exclude_unset=True)
        for field in current_data:
            if field in update_data:
                setattr(current_object_model, field, update_data[field])

        async with async_session.begin():
            async_session.add(current_object_model)
        await async_session.refresh(current_object_model)
        return current_object_model

    async def remove_by_id(self, async_session: AsyncSession, *, id: int) -> ModelType:
        object_model = await self.get_by_id(async_session, id=id)
        async with async_session.begin():
            await async_session.delete(object_model)
        return object_model
