import asyncio
from asyncio import BaseEventLoop as AsyncLoopType
from functools import partial
from typing import TYPE_CHECKING

import inject

from mw_url_shortener.interfaces.redirect_interface import RedirectInterface
from mw_url_shortener.interfaces.user_interface import UserInterface
from mw_url_shortener.settings import Settings

from .interfaces import inject_interface, inject_resource
from .settings import get_settings, inject_settings

if TYPE_CHECKING:
    from typing import List, Optional, Sequence

    from mw_url_shortener.interfaces.base import OpenedResourceT, ResourceT


def inject_loop(binder: inject.Binder, *, loop: AsyncLoopType) -> None:
    binder.bind(AsyncLoopType, loop)


def get_async_loop() -> AsyncLoopType:
    return inject.instance(AsyncLoopType)


def install_configurators(
    binder: inject.Binder, *, configurators: "List[inject.BinderCallable]"
) -> None:
    for configurator in configurators:
        binder.install(configurator)


def initialize_dependency_injection(
    configurators: "Optional[List[inject.BinderCallable]]" = None,
) -> None:
    if configurators is None:
        configurators = []

    settings = Settings()
    settings_injector = partial(inject_settings, settings=settings)
    configurators.append(settings_injector)

    loop = asyncio.get_running_loop()
    loop_injector = partial(inject_loop, loop=loop)
    configurators.append(loop_injector)

    inject.configure(partial(install_configurators, configurators=configurators))


def reconfigure_dependency_injection(
    resource: "ResourceT",
    user_interface: "UserInterface[OpenedResourceT]",
    redirect_interface: "RedirectInterface[OpenedResourceT]",
    settings: "Optional[Settings]" = None,
    loop: "Optional[AsyncLoopType]" = None,
    configurators: "Optional[List[inject.BinderCallable]]" = None,
) -> None:
    if settings is None:
        settings = get_settings()
    settings_injector = partial(inject_settings, settings=settings)

    if loop is None:
        loop = inject.instance(AsyncLoopType)
    loop_injector = partial(inject_loop, loop=loop)

    resource_injector = partial(inject_resource, resource=resource)

    user_interface_injector = partial(
        inject_interface,
        interface_type=UserInterface,
        interface=user_interface,
    )

    redirect_interface_injector = partial(
        inject_interface,
        interface_type=RedirectInterface,
        interface=redirect_interface,
    )

    if configurators is None:
        configurators = []

    configurators.extend(
        [
            loop_injector,
            settings_injector,
            resource_injector,
            user_interface_injector,
            redirect_interface_injector,
        ]
    )
    inject.clear_and_configure(
        partial(
            install_configurators,
            configurators=configurators,
        )
    )
