# mypy: allow_any_expr
from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import select, update

from mw_url_shortener.database.models.base import DeclarativeBase
from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.interfaces.base import (
    CreateSchemaType,
    InterfaceBase,
    ObjectSchemaType,
    UpdateSchemaType,
)

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class DBInterfaceBase(
    InterfaceBase[
        AsyncSession,
        ObjectSchemaType,
        CreateSchemaType,
        UpdateSchemaType,
    ],
):
    def __init__(self, model: Type[ModelType], schema: Type[ObjectSchemaType]):
        """
        interface object with default methods to create, read, update, delete
        """
        self.model = model
        self.schema = schema

    async def get_by_id(
        self, opened_resource: AsyncSession, /, *, id: int
    ) -> Optional[ObjectSchemaType]:
        async with opened_resource.begin():
            object_model = (
                await opened_resource.execute(
                    select(self.model).where(self.model.id == id)
                )
            ).scalar_one_or_none()

            if object_model is None:
                return None

            assert isinstance(
                object_model, self.model
            ), f"expected '{self.model}', got '{type(object_model)}'"
            return self.schema.from_orm(object_model)

    async def get_multiple(
        self, opened_resource: AsyncSession, /, *, skip: int = 0, limit: int = 100
    ) -> List[ObjectSchemaType]:
        objects: List[ObjectSchemaType] = []
        async with opened_resource.begin():
            query = select(self.model).offset(skip).limit(limit)
            object_models = (await opened_resource.execute(query)).scalars().all()
            for object_model in object_models:
                objects.append(self.schema.from_orm(object_model))
        return objects

    async def create(
        self,
        opened_resource: AsyncSession,
        /,
        *,
        create_object_schema: CreateSchemaType,
    ) -> ObjectSchemaType:
        object_model = self.model(**create_object_schema.dict())
        async with opened_resource.begin():
            opened_resource.add(object_model)
        await opened_resource.refresh(object_model)
        await opened_resource.close()  # .refresh() opens a new session
        return self.schema.from_orm(object_model)

    async def update(
        self,
        opened_resource: AsyncSession,
        /,
        *,
        current_object_schema: ObjectSchemaType,
        update_object_schema: UpdateSchemaType,
    ) -> Optional[ObjectSchemaType]:
        update_data = update_object_schema.dict(exclude_unset=True)
        updated_object = current_object_schema.copy(exclude={"id"}, update=update_data)
        new_object_data = updated_object.dict(exclude_none=True)

        if not new_object_data:
            return current_object_schema

        get_by_id = select(self.model).where(self.model.id == current_object_schema.id)
        async with opened_resource.begin():
            object_model = (await opened_resource.execute(get_by_id)).scalar_one_or_none()

            if object_model is None:
                return None

            update_sql = (
                update(self.model)
                .where(self.model.id == current_object_schema.id)
                .values(**new_object_data)
                .execution_options(synchronize_session="evaluate")
            )
            await opened_resource.execute(update_sql)
            return self.schema.from_orm(object_model)

    async def remove_by_id(
        self, opened_resource: AsyncSession, /, *, id: int
    ) -> ObjectSchemaType:
        async with opened_resource.begin():
            get_by_id = select(self.model).where(self.model.id == id)
            object_model = (await opened_resource.execute(get_by_id)).scalar_one()
            object_schema = self.schema.from_orm(object_model)
            await opened_resource.delete(object_model)
            object_schema_with_id = object_schema.copy(update={"id": id})
            return object_schema_with_id
