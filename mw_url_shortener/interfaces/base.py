from abc import abstractmethod
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


class ImmutableInterfaceBase(
    Generic[OpenedResourceT, ObjectSchemaType, CreateSchemaType]
):
    """
    generic immutable base interface for concrete implementations of database
    and api interactions
    """


class InterfaceBase(
    ImmutableInterfaceBase[OpenedResourceT, ObjectSchemaType, CreateSchemaType],
    Generic[OpenedResourceT, ObjectSchemaType, CreateSchemaType, UpdateSchemaType],
):
    """
    generic mutable base interface for concrete implementations of database and
    api access
    """


CovariantObjectSchemaType = TypeVar(
    "CovariantObjectSchemaType", bound=BaseSchema, covariant=True
)

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
class ImmutableInterfaceBaseProtocol(
    Protocol[
        ContravariantOpenedResourceT,
        CovariantObjectSchemaType,
        ContravariantCreateSchemaType,
    ]
):
    """
    generic immutable base interface for abstracting database and api
    interactions
    """

    @abstractmethod
    async def create(
        self,
        opened_resource: OpenedResourceT,
        /,
        *,
        create_object_schema: CreateSchemaType,
    ) -> Optional[CovariantObjectSchemaType]:
        raise NotImplementedError

    @abstractmethod
    async def remove_by_id(
        self, opened_resource: OpenedResourceT, /, *, id: int
    ) -> Optional[CovariantObjectSchemaType]:
        raise NotImplementedError


@runtime_checkable
class InterfaceBaseProtocol(
    ImmutableInterfaceBaseProtocol[
        ContravariantOpenedResourceT, ObjectSchemaType, CreateSchemaType
    ],
    Protocol[
        ContravariantOpenedResourceT,
        ObjectSchemaType,
        CreateSchemaType,
        ContravariantUpdateSchemaType,
    ],
):
    "generic base interface for abstracting database and api access"

    @abstractmethod
    async def update(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        current_object_schema: ObjectSchemaType,
        update_object_schema: ContravariantUpdateSchemaType,
    ) -> Optional[ObjectSchemaType]:
        raise NotImplementedError
