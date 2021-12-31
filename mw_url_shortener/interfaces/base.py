from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, Union

from mw_url_shortener.schemas.base import BaseInDBSchema, BaseSchema

if TYPE_CHECKING:
    from httpx import AsyncClient

    from mw_url_shortener.database.start import AsyncSession, sessionmaker


Resource = TypeVar("Resource", "sessionmaker[AsyncSession]", "AsyncClient")
ResourceType = Union["sessionmaker[AsyncSession]", "AsyncClient"]
OpenedResource = TypeVar("OpenedResource", bound=Union["AsyncSession", "AsyncClient"])
OpenedResourceType = Union["AsyncSession", "AsyncClient"]
ObjectSchemaType = TypeVar("ObjectSchemaType", bound=BaseInDBSchema)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class InterfaceBase(
    Generic[Resource, ObjectSchemaType, CreateSchemaType, UpdateSchemaType]
):
    """
    generic base interface for concrete implementations of database and api
    access
    """


class InterfaceBaseProtocol(Protocol):
    "generic base interface for abstracting database and api access"
