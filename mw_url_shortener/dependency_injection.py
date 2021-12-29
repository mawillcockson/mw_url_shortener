# mypy: allow_any_expr
import asyncio
from asyncio import BaseEventLoop as AsyncLoopType
from functools import partial
from typing import List, Optional

import inject

from mw_url_shortener.settings import Settings

__all__ = [
    "inject_settings",
    "inject_loop",
    "initialize_dependency_injection",
    "reconfigure_dependency_injection",
    "AsyncLoopType",
]


def inject_settings(binder: inject.Binder, *, settings: Settings) -> None:
    binder.bind(Settings, settings)


def inject_loop(binder: inject.Binder, *, loop: AsyncLoopType) -> None:
    binder.bind(AsyncLoopType, loop)


def install_configurators(
    binder: inject.Binder, *, configurators: List[inject.BinderCallable]
) -> None:
    for configurator in configurators:
        binder.install(configurator)


def initialize_dependency_injection(
    configurators: Optional[List[inject.BinderCallable]] = None,
) -> None:
    if configurators is None:
        configurators = []

    settings = Settings()
    configurators.append(partial(inject_settings, settings=settings))

    loop = asyncio.get_running_loop()
    configurators.append(partial(inject_loop, loop=loop))

    inject.configure(partial(install_configurators, configurators=configurators))


def reconfigure_dependency_injection(
    configurators: Optional[List[inject.BinderCallable]] = None,
    *,
    settings: Optional[Settings] = None,
    loop: Optional[AsyncLoopType] = None
) -> None:
    if configurators is None:
        configurators = []

    if settings is None:
        settings = inject.instance(Settings)
    configurators.append(partial(inject_settings, settings=settings))

    if loop is None:
        loop = inject.instance(AsyncLoopType)
    configurators.append(partial(inject_loop, loop=loop))

    inject.clear_and_configure(
        partial(install_configurators, configurators=configurators)
    )
