import asyncio
from asyncio import BaseEventLoop as AsyncLoopType
from functools import partial
from typing import TYPE_CHECKING

import inject

from mw_url_shortener.settings import Settings

from .settings import get_settings, inject_settings

if TYPE_CHECKING:
    from typing import List, Optional, Sequence


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
    configurators: "Optional[List[inject.BinderCallable]]" = None,
    *,
    settings: "Optional[Settings]" = None,
    loop: "Optional[AsyncLoopType]" = None,
) -> None:
    if configurators is None:
        configurators = []

    if settings is None:
        settings = get_settings()
    configurators.append(partial(inject_settings, settings=settings))

    if loop is None:
        loop = inject.instance(AsyncLoopType)
    configurators.append(partial(inject_loop, loop=loop))

    inject.clear_and_configure(
        partial(install_configurators, configurators=configurators)
    )


def install_binder_callables(
    binder: "inject.Binder",
    *,
    configurators: "Optional[Sequence[inject.BinderCallable]]" = None,
) -> None:
    if not configurators:
        return

    for configurator in configurators:
        binder.install(configurator)
