from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

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

    async def get_by_id(
        self, async_session: AsyncSession, id: Any
    ) -> Optional[ModelType]:
        async with async_session() as session:
            user_model = await session.get(self.model, id)
        return user_model

    async def get_multiple(
        self, async_session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        async with async_session() as session:
            async with session.begin():
                user_models = (
                    (
                        await session.execute(
                            select(self.model).offset(skip).limit(limit)
                        )
                    )
                    .scalars()
                    .all()
                )
            for user_model in user_models:
                await session.refresh(user_model)
            return user_models

    async def create(
        self, async_session: AsyncSession, *, object_schema_in: CreateSchemaType
    ) -> ModelType:
        object_in_data = jsonable_encoder(object_schema_in)
        object_model = self.model(**object_in_data)  # type: ignore
        async with async_session() as session:
            async with session.begin():
                session.add(object_model)
            await session.refresh(object_model)
        return object_model

    async def update(
        self,
        async_session: AsyncSession,
        *,
        current_object_model: ModelType,
        object_update_schema: UpdateSchemaType,
    ) -> ModelType:
        current_data = jsonable_encoder(current_object_model)
        if isinstance(object_update_schema, dict):
            update_data = object_update_schema
        else:
            update_data = object_update_schema.dict(exclude_unset=True)
        for field in current_data:
            if field in update_data:
                setattr(current_object_model, field, update_data[field])

        async with async_session() as session:
            async with session.begin():
                session.add(current_object_model)
            await session.refresh(current_object_model)
        return current_object_model

    async def remove_by_id(self, async_session: AsyncSession, *, id: int) -> ModelType:
        object_model = await self.get_by_id(async_session, id=id)
        async with async_session() as session:
            async with session.begin():
                await session.delete(object_model)
        return object_model
