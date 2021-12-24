import inject
from typing import List, Optional
from asyncio import BaseEventLoop as AsyncLoopType
from mw_url_shortener.settings import Settings
import asyncio
from functools import partial


def inject_settings(binder: inject.Binder, *, settings: Settings) -> None:
    binder.bind(Settings, settings)


def inject_loop(binder: inject.Binder, *, loop: AsyncLoopType) -> None:
    binder.bind(AsyncLoopType, loop)


def initialize_depency_injection(configurators: List[inject.BinderCallable] = []) -> None:
    settings = Settings()
    configurators.append(partial(inject_settings, settings=settings))

    loop = asyncio.get_running_loop()
    configurators.append(partial(inject_loop, loop=loop))

    def config(binder: inject.Binder) -> None:
        for configurator in configurators:
            binder.install(configurator)

    inject.configure(config)


def reconfigure_dependency_injection(configurators: List[inject.BinderCallable] = [], *, settings: Optional[Settings] = None, loop: Optional[AsyncLoopType] = None) -> None:
    if settings is None:
        settings = inject.instance(Settings)
    configurators.append(partial(inject_settings, settings=settings))

    if loop is None:
        loop = inject.instance(AsyncLoopType)
    configurators.append(partial(inject_loop, loop=loop))

    def config(binder: inject.Binder) -> None:
        for configurator in configurators:
            binder.install(configurator)

    inject.clear_and_configure(config)