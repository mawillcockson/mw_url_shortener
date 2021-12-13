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

    async def get_by_id(self, async_session: AsyncSession, id: Any) -> Optional[ModelType]:
        return await async_session.get(User, id)
        # in cases where the id is not the primary key
        # return (
        #     await async_session.execute(select(self.model).where(self.model.id == id))
        #     .scalars()
        #     .first()
        # )

    async def get_multiple(
        self, async_session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return await async_session.execute(select(self.model).offset(skip).limit(limit)).all()

    async def create(
        self, async_session: AsyncSession, *, object_schema_in: CreateSchemaType
    ) -> ModelType:
        object_in_data = jsonable_encoder(object_schema_in)
        object_model = self.model(**object_in_data)  # type: ignore
        # async with async_session() as active_session:
        #     async with async_session.begin():
        await async_session.add(object_model)
        await async_session.commit()
        await async_session.refresh(object_model)
        return object_model

    async def update(
        self,
        async_session: AsyncSession,
        *,
        current_object_model: ModelType,
        update_object_schema: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        object_data = jsonable_encoder(object_model)
        if isinstance(update_object_schema, dict):
            update_data = update_object_schema
        else:
            update_data = update_object_schema.dict(exclude_unset=True)
        for field in object_data:
            if field in update_data:
                setattr(object_model, field, update_data[field])

        await async_session.add(object_model)
        await async_session.commit()
        await async_session.refresh(object_model)
        return object_model

    async def remove_by_id(self, async_session: AsyncSession, *, id: int) -> ModelType:
        object_model = await self.get_by_id(async_session, id=id)
        await async_session.delete(object_model)
        await async_session.commit()
        return object_model
