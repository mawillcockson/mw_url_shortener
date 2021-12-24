import asyncio
import sys
from functools import partial
from pathlib import Path

import inject
import typer

from mw_url_shortener.database.start import inject_async_sessionmaker, make_sessionmaker
from mw_url_shortener.dependency_injection import (
    AsyncLoopType,
    reconfigure_dependency_injection,
)
from mw_url_shortener.interfaces import UserInterface
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.interfaces import inject_interface, inject_resource
from mw_url_shortener.settings import CliMode, Settings, defaults

from .user import app as user_app


def callback(
    ctx: typer.Context,
    database_path: Path = typer.Option(defaults.database_path),
) -> None:
    if ctx.resilient_parsing or ctx.invoked_subcommand is None or "--help" in sys.argv:
        return

    settings = inject.instance(Settings)
    settings.cli_mode = CliMode.local_database
    settings.database_path = database_path

    loop = inject.instance(AsyncLoopType)
    async_sessionmaker = asyncio.run_coroutine_threadsafe(
        make_sessionmaker(settings.database_url), loop=loop
    ).result()
    async_sessionmaker_injector = partial(
        inject_async_sessionmaker, async_sessionmaker=async_sessionmaker
    )
    resource_injector = partial(inject_resource, resource=async_sessionmaker)

    interface_injector = partial(
        inject_interface,
        interface_type=UserInterface,
        interface=database_interface.user,
    )

    reconfigure_dependency_injection(
        [async_sessionmaker_injector, resource_injector, interface_injector]
    )


app = typer.Typer(callback=callback)

app.add_typer(user_app, name="user")
