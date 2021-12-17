# mypy: allow_any_expr
from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener.database.models.base import DeclarativeBase
from mw_url_shortener.schemas.base import BaseInDBSchema, BaseSchema

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
ObjectSchemaType = TypeVar("ObjectSchemaType", bound=BaseInDBSchema)
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
                await async_session.execute(
                    select(self.model).where(self.model.id == id)
                )
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
        self,
        async_session: AsyncSession,
        *,
        create_object_schema: CreateSchemaType,
    ) -> ObjectSchemaType:
        object_model = self.model(**create_object_schema.dict(exclude_unset=True))
        async with async_session.begin():
            async_session.add(object_model)
        await async_session.refresh(object_model)
        await async_session.close()  # .refresh() opens a new session
        return self.schema.from_orm(object_model)

    async def update(
        self,
        async_session: AsyncSession,
        *,
        current_object_schema: ObjectSchemaType,
        update_object_schema: UpdateSchemaType,
    ) -> ObjectSchemaType:
        update_data = update_object_schema.dict(exclude_unset=True)
        updated_object = current_object_schema.copy(exclude={"id"}, update=update_data)

        get_by_id = select(self.model).where(self.model.id == current_object_schema.id)
        async with async_session.begin():
            object_model = (await async_session.execute(get_by_id)).scalar_one()
            update_sql = (
                update(self.model)
                .where(self.model.id == current_object_schema.id)
                .values(**updated_object.dict())
                .execution_options(synchronize_session="evaluate")
            )
            await async_session.execute(update_sql)
            return self.schema.from_orm(object_model)

    async def remove_by_id(
        self, async_session: AsyncSession, *, id: int
    ) -> ObjectSchemaType:
        async with async_session.begin():
            get_by_id = select(self.model).where(self.model.id == id)
            object_model = (await async_session.execute(get_by_id)).scalar_one()
            object_schema = self.schema.from_orm(object_model)
            await async_session.delete(object_model)
            object_schema_with_id = object_schema.copy(update={"id": id})
            return object_schema_with_id
