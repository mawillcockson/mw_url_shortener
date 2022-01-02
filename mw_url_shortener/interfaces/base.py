from typing import (
    TYPE_CHECKING,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

from mw_url_shortener.schemas.base import BaseInDBSchema, BaseSchema

if TYPE_CHECKING:
    from httpx import AsyncClient

    from mw_url_shortener.database.start import AsyncSession, sessionmaker


ResourceT = TypeVar("ResourceT", "sessionmaker[AsyncSession]", "AsyncClient")
Resource = Union["sessionmaker[AsyncSession]", "AsyncClient"]
OpenedResourceT = TypeVar("OpenedResourceT", "AsyncSession", "AsyncClient")
OpenedResource = Union["AsyncSession", "AsyncClient"]
ObjectSchemaType = TypeVar("ObjectSchemaType", bound=BaseInDBSchema)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class InterfaceBase(
    Generic[OpenedResourceT, ObjectSchemaType, CreateSchemaType, UpdateSchemaType]
):
    """
    generic base interface for concrete implementations of database and api
    access
    """


ContravariantOpenedResourceT = TypeVar(
    "ContravariantOpenedResourceT", "AsyncSession", "AsyncClient", contravariant=True
)
ContravariantCreateSchemaType = TypeVar(
    "ContravariantCreateSchemaType", bound=BaseSchema, contravariant=True
)
ContravariantUpdateSchemaType = TypeVar(
    "ContravariantUpdateSchemaType", bound=BaseSchema, contravariant=True
)


@runtime_checkable
class InterfaceBaseProtocol(
    Protocol[
        ContravariantOpenedResourceT,
        ObjectSchemaType,
        ContravariantCreateSchemaType,
        ContravariantUpdateSchemaType,
    ]
):
    "generic base interface for abstracting database and api access"

    async def create(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        create_object_schema: ContravariantCreateSchemaType,
    ) -> Optional[ObjectSchemaType]:
        ...

    async def get_by_id(
        self, opened_resource: ContravariantOpenedResourceT, /, *, id: int
    ) -> Optional[ObjectSchemaType]:
        ...

    async def update(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        current_object_schema: ObjectSchemaType,
        update_object_schema: ContravariantUpdateSchemaType,
    ) -> Optional[ObjectSchemaType]:
        ...

    async def remove_by_id(
        self, opened_resource: ContravariantOpenedResourceT, /, *, id: int
    ) -> Optional[ObjectSchemaType]:
        ...
