import asyncio
from contextlib import AsyncExitStack, contextmanager
from typing import (
    Awaitable,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

import inject
from httpx import AsyncClient

from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.dependency_injection import get_async_loop, get_settings
from mw_url_shortener.settings import CliMode, Settings

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
from .redirect_interface import RedirectInterface
from .user_interface import UserInterface

T = TypeVar("T")


def run_sync(coroutine: Awaitable[T]) -> T:
    loop = get_async_loop()
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

        loop = get_async_loop()
        future = asyncio.run_coroutine_threadsafe(
            get_async_session(async_sessionmaker), loop=loop
        )
        result = future.result()
        async_exitstack, async_session = result

        yield async_session

        asyncio.run_coroutine_threadsafe(async_exitstack.aclose(), loop=loop).result()


open_resource = contextmanager(resource_opener)


def get_resource(resource_type: Optional[Type[ResourceT]] = None) -> ResourceT:
    if resource_type is None:
        settings = get_settings()
        if settings.cli_mode == CliMode.local_database:
            return cast("ResourceT", inject.instance("sessionmaker[AsyncSession]"))
        return cast("ResourceT", inject.instance("AsyncClient"))

    return inject.instance(resource_type)


def inject_resource(binder: "inject.Binder", *, resource: ResourceT) -> None:
    binder.bind(Resource, resource)


def inject_interface(
    binder: "inject.Binder",
    *,
    interface_type: Type[
        InterfaceBaseProtocol[
            ContravariantOpenedResourceT,
            ObjectSchemaType,
            ContravariantCreateSchemaType,
            ContravariantUpdateSchemaType,
        ]
    ],
    interface: InterfaceBaseProtocol[
        ContravariantOpenedResourceT,
        ObjectSchemaType,
        ContravariantCreateSchemaType,
        ContravariantUpdateSchemaType,
    ],
) -> None:
    binder.bind(interface_type, interface)


def get_user_interface(
    interface_type: Optional[Type[UserInterface[ContravariantOpenedResourceT]]] = None,
) -> UserInterface[ContravariantOpenedResourceT]:
    if interface_type is None:
        user_interface = inject.instance(UserInterface)
    else:
        user_interface = inject.instance(interface_type)

    assert isinstance(
        user_interface, UserInterface
    ), f"{user_interface} is not UserInterface"
    return user_interface


def get_redirect_interface(
    interface_type: Optional[
        Type[RedirectInterface[ContravariantOpenedResourceT]]
    ] = None,
) -> RedirectInterface[ContravariantOpenedResourceT]:
    if interface_type is None:
        redirect_interface = inject.instance(RedirectInterface)
    else:
        redirect_interface = inject.instance(interface_type)

    assert isinstance(
        redirect_interface, RedirectInterface
    ), f"{redirect_interface} is not RedirectInterface"
    return redirect_interface


def install_binder_callables(
    binder: "inject.Binder",
    *,
    configurators: "Optional[Sequence[inject.BinderCallable]]" = None,
) -> None:
    if not configurators:
        return

    for configurator in configurators:
        binder.install(configurator)
