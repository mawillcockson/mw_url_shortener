import asyncio
from contextlib import AsyncExitStack, contextmanager
from typing import ContextManager, Iterator, Tuple, Type, Union, overload

import inject
from httpx import AsyncClient

from mw_url_shortener import database_interface
from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.database_interface.base import (
    CreateSchemaType,
    ObjectSchemaType,
    UpdateSchemaType,
)
from mw_url_shortener.dependency_injection import AsyncLoopType

ResourceType = Union["sessionmaker[AsyncSession]", AsyncClient]


def run_sync(coroutine) -> "whatever the return type of the coroutine is":
    loop = inject.instance(AsyncLoopType)
    return asyncio.run_coroutine_threadsafe(coroutine, loop=loop).result()


@overload
def open_resource(resource: AsyncClient) -> ContextManager[AsyncClient]:
    ...


@overload
def open_resource(
    resource: "sessionmaker[AsyncSession]",
) -> ContextManager[AsyncSession]:
    ...


def open_resource(resource):
    if isinstance(resource, sessionmaker):
        async_sessionmaker = inject.instance("sessionmaker[AsyncSession]")

        @contextmanager
        def get_async_resource() -> Iterator[AsyncSession]:
            async def get_async_session(
                async_sessionmaker: "sessionmaker[AsyncSession]",
            ) -> Tuple[AsyncExitStack, AsyncSession]:
                async with AsyncExitStack() as stack:
                    async_session = await stack.enter_async_context(
                        async_sessionmaker()
                    )
                    return (stack.pop_all(), async_session)

            loop = inject.instance(AsyncLoopType)
            async_exitstack, async_session = asyncio.run_coroutine_threadsafe(
                get_async_session(async_sessionmaker), loop=loop
            ).result()

            yield async_session

            asyncio.run_coroutine_threadsafe(
                async_exitstack.aclose(), loop=loop
            ).result()

    elif isinstance(self.resource, AsyncClient):
        async_client = inject.instance(AsyncClient)

        @contextmanager
        def get_async_resource() -> Iterator[AsyncClient]:
            yield async_client

    else:
        raise TypeError(f"unkown resource type: '{type(self.resource)}'")

    return get_async_resource()


class BaseInterface:
    def __init__(self, resource: ResourceType):
        self.resource = resource

    def create(self, create_object_schema: CreateSchemaType) -> ObjectSchemaType:
        with open_resource(self.resource) as resource:
            return run_sync(
                self.interface.create(
                    resource, create_object_schema=create_object_schema
                )
            )


def inject_interface(
    binder: "inject.Binder",
    *,
    interface_type: Type[BaseInterface],
    interface: BaseInterface,
) -> None:
    binder.bind(interface_type, interface)
