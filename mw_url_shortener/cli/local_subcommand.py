import asyncio
import sys
from functools import partial
from pathlib import Path

import inject
import typer

from mw_url_shortener.database.start import inject_async_sessionmaker, make_sessionmaker
from mw_url_shortener.dependency_injection import (
    AsyncLoopType,
    get_settings,
    reconfigure_dependency_injection,
)
from mw_url_shortener.interfaces import RedirectInterface, UserInterface
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.interfaces import inject_interface, inject_resource
from mw_url_shortener.settings import CliMode, Settings, defaults

from .common_subcommands import SHOW_CONFIGURATION_COMMAND_NAME, show_configuration
from .redirect import app as redirect_app
from .user import app as user_app


def callback(
    ctx: typer.Context,
    database_path: Path = typer.Option(defaults.database_path),
    log_db_access: bool = typer.Option(
        defaults.log_db_access, help="show output from the database interactions"
    ),
) -> None:
    if ctx.resilient_parsing or ctx.invoked_subcommand is None or "--help" in sys.argv:
        return

    settings = get_settings()
    settings.cli_mode = CliMode.local_database
    settings.database_path = database_path
    settings.log_db_access = log_db_access

    if ctx.invoked_subcommand == SHOW_CONFIGURATION_COMMAND_NAME:
        return

    loop = inject.instance(AsyncLoopType)
    async_sessionmaker = asyncio.run_coroutine_threadsafe(
        make_sessionmaker(settings.database_url, echo=log_db_access), loop=loop
    ).result()
    async_sessionmaker_injector = partial(
        inject_async_sessionmaker, async_sessionmaker=async_sessionmaker
    )
    resource_injector = partial(inject_resource, resource=async_sessionmaker)

    if ctx.invoked_subcommand == "user":
        interface_injector = partial(
            inject_interface,
            interface_type=UserInterface,
            interface=database_interface.user,
        )

    if ctx.invoked_subcommand == "redirect":
        interface_injector = partial(
            inject_interface,
            interface_type=RedirectInterface,
            interface=database_interface.redirect,
        )

    reconfigure_dependency_injection(
        [async_sessionmaker_injector, resource_injector, interface_injector]
    )


app = typer.Typer(callback=callback)
app.command(name=SHOW_CONFIGURATION_COMMAND_NAME)(show_configuration)

app.add_typer(user_app, name="user")
app.add_typer(redirect_app, name="redirect")
