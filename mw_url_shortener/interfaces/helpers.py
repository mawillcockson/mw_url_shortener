# mypy: allow_any_expr
import asyncio
from contextlib import AsyncExitStack, contextmanager
from typing import Awaitable, Iterator, Tuple, Type, TypeVar, Union, cast, overload, Optional

import inject
from httpx import AsyncClient

from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.dependency_injection import AsyncLoopType
from mw_url_shortener.settings import Settings, CliMode

from .base import (
    CreateSchemaType,
    InterfaceBase,
    ObjectSchemaType,
    OpenedResource,
    OpenedResourceType,
    Resource,
    ResourceType,
    UpdateSchemaType,
)

T = TypeVar("T")


def run_sync(coroutine: Awaitable[T]) -> T:
    loop = inject.instance(AsyncLoopType)
    return asyncio.run_coroutine_threadsafe(coroutine, loop=loop).result()


@overload
def resource_opener(resource: "sessionmaker[AsyncSession]") -> "Iterator[AsyncSession]":
    ...


@overload
def resource_opener(resource: "AsyncClient") -> "Iterator[AsyncClient]":
    ...


def resource_opener(resource: ResourceType) -> Iterator[OpenedResourceType]:
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
        future = asyncio.run_coroutine_threadsafe(
            get_async_session(async_sessionmaker), loop=loop
        )
        result = future.result()
        async_exitstack, async_session = result

        yield async_session

        asyncio.run_coroutine_threadsafe(async_exitstack.aclose(), loop=loop).result()


open_resource = contextmanager(resource_opener)


def get_resource(resource_type: Optional[Type[Resource]] = None) -> Resource:
    if resource_type is None:
        settings = inject.instance(Settings)
        if settings.cli_mode == CliMode.local_database:
            return cast("Resource", inject.instance("sessionmaker[AsyncSession]"))
        return cast("Resource", inject.instance("AsyncClient"))

    return inject.instance(resource_type)


def inject_interface(
    binder: "inject.Binder",
    *,
    interface_type: Type[
        InterfaceBase[Resource, ObjectSchemaType, CreateSchemaType, UpdateSchemaType]
    ],
    interface: InterfaceBase[
        Resource, ObjectSchemaType, CreateSchemaType, UpdateSchemaType
    ],
) -> None:
    binder.bind(interface_type, interface)


def inject_resource(binder: "inject.Binder", *, resource: ResourceType) -> None:
    binder.bind(ResourceType, resource)
