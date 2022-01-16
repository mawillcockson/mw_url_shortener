import asyncio
from asyncio import BaseEventLoop as AsyncLoopType
from contextlib import AsyncExitStack, contextmanager
from typing import Awaitable, Iterator, Tuple, TypeVar, overload

import inject
from httpx import AsyncClient

from mw_url_shortener.database.start import AsyncSession, sessionmaker

from .base import (
    ContravariantCreateSchemaType,
    ContravariantOpenedResourceT,
    ContravariantUpdateSchemaType,
    InterfaceBaseProtocol,
    ObjectSchemaType,
    OpenedResource,
    Resource,
    ResourceT,
)

T = TypeVar("T")


def run_sync(coroutine: Awaitable[T]) -> T:
    # cannot mw_url_shortener.dependency_injection.main.get_async_loop because of a circular import
    # loop = get_async_loop()
    loop = inject.instance(AsyncLoopType)
    return asyncio.run_coroutine_threadsafe(coroutine, loop=loop).result()


@overload
def resource_opener(resource: "sessionmaker[AsyncSession]") -> "Iterator[AsyncSession]":
    ...


@overload
def resource_opener(resource: "AsyncClient") -> "Iterator[AsyncClient]":
    ...


def resource_opener(resource: Resource) -> Iterator[OpenedResource]:
    if isinstance(resource, AsyncClient):  # type: ignore
        yield resource

    else:
        async_sessionmaker = resource

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

        try:
            yield async_session
        finally:
            asyncio.run_coroutine_threadsafe(
                async_exitstack.aclose(), loop=loop
            ).result()


open_resource = contextmanager(resource_opener)
