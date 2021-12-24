# mypy: allow_any_expr
import asyncio
from contextlib import AsyncExitStack, contextmanager
from typing import Awaitable, Iterator, Tuple, Type, TypeVar, Union, cast, overload

import inject
from httpx import AsyncClient

from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.dependency_injection import AsyncLoopType

from .base import (
    CreateSchemaType,
    InterfaceBase,
    ObjectSchemaType,
    Resource,
    ResourceType,
    UpdateSchemaType,
)

T = TypeVar("T")


def run_sync(coroutine: Awaitable[T]) -> T:
    loop = inject.instance(AsyncLoopType)
    return asyncio.run_coroutine_threadsafe(coroutine, loop=loop).result()


@overload
def resource_opener(resource: "sessionmaker[AsyncSession]") -> Iterator[AsyncSession]:
    ...


@overload
def resource_opener(resource: AsyncClient) -> Iterator[AsyncClient]:
    ...


def resource_opener(resource: Resource) -> Iterator[Union[AsyncClient, AsyncSession]]:
    if isinstance(resource, AsyncClient):
        async_client = inject.instance(AsyncClient)
        yield async_client

    else:
        async_sessionmaker = cast(
            "sessionmaker[AsyncSession]", inject.instance("sessionmaker[AsyncSession]")
        )

        async def get_async_session(
            async_sessionmaker: "sessionmaker[AsyncSession]",
        ) -> Tuple[AsyncExitStack, AsyncSession]:
            async with AsyncExitStack() as stack:
                async_session = await stack.enter_async_context(async_sessionmaker())
                return (stack.pop_all(), async_session)

        loop = inject.instance(AsyncLoopType)
        async_exitstack, async_session = asyncio.run_coroutine_threadsafe(
            get_async_session(async_sessionmaker), loop=loop
        ).result()

        yield async_session

        asyncio.run_coroutine_threadsafe(async_exitstack.aclose(), loop=loop).result()


open_resource = contextmanager(resource_opener)


def inject_interface(
    binder: "inject.Binder",
    *,
    interface_type: Type[
        InterfaceBase[
            ResourceType, ObjectSchemaType, CreateSchemaType, UpdateSchemaType
        ]
    ],
    interface: InterfaceBase[
        ResourceType, ObjectSchemaType, CreateSchemaType, UpdateSchemaType
    ],
) -> None:
    binder.bind(interface_type, interface)


def inject_resource(binder: "inject.Binder", *, resource: Resource) -> None:
    binder.bind(Resource, resource)


# from abc import ABC, abstractmethod
# from .database.base import ModelType
# class BaseInterface(ABC, Generic[ResourceType]):
#     def __init__(self, resource: ResourceType):
#         self.resource = resource
#
#     @property
#     @abstractmethod
#     def interface(
#         self,
#     ) -> InterfaceBase[ModelType, ObjectSchemaType, CreateSchemaType, UpdateSchemaType]:
#         raise NotImplementedError
#
#     def create(self, create_object_schema: CreateSchemaType) -> ObjectSchemaType:
#         with open_resource(self.resource) as resource:
#             return run_sync(
#                 self.interface.create(
#                     resource, create_object_schema=create_object_schema
#                 )
#             )

# from httpx import AsyncClient
#
# from mw_url_shortener import database_interface
#
# from .base import BaseInterface, ResourceType
#
#
# class UserInterface(BaseInterface):
#     @property
#     def interface(self) -> ResourceType:
#         if isinstance(self.resource, AsyncClient):
#             raise NotImplementedError
#         return database_interface.user
