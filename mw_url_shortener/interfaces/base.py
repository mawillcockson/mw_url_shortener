from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, Union

from mw_url_shortener.schemas.base import BaseInDBSchema, BaseSchema

if TYPE_CHECKING:
    from httpx import AsyncClient

    from mw_url_shortener.database.start import AsyncSession, sessionmaker


ResourceT = TypeVar("ResourceT", "sessionmaker[AsyncSession]", "AsyncClient")
Resource = Union["sessionmaker[AsyncSession]", "AsyncClient"]
OpenedResourceT = TypeVar("OpenedResourceT", bound=Union["AsyncSession", "AsyncClient"])
OpenedResource = Union["AsyncSession", "AsyncClient"]
ObjectSchemaType = TypeVar("ObjectSchemaType", bound=BaseInDBSchema)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class InterfaceBase(
    Generic[ResourceT, ObjectSchemaType, CreateSchemaType, UpdateSchemaType]
):
    """
    generic base interface for concrete implementations of database and api
    access
    """


class InterfaceBaseProtocol(Protocol):
    "generic base interface for abstracting database and api access"
