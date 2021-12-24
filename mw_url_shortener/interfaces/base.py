from typing import TYPE_CHECKING, Generic, TypeVar

from mw_url_shortener.schemas.base import BaseInDBSchema, BaseSchema

if TYPE_CHECKING:
    from httpx import AsyncClient

    from mw_url_shortener.database.start import AsyncSession, sessionmaker

ResourceType = TypeVar("ResourceType", "sessionmaker[AsyncSession]", "AsyncClient")
ObjectSchemaType = TypeVar("ObjectSchemaType", bound=BaseInDBSchema)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class InterfaceBase(
    Generic[ResourceType, ObjectSchemaType, CreateSchemaType, UpdateSchemaType]
):
    "generic base interface for abstracting database and api access"
