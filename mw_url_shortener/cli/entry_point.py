"the main cli entrypoint"
import sys
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import inject
import typer

from mw_url_shortener import __version__
from mw_url_shortener.settings import Settings, defaults

if TYPE_CHECKING:
    from typing import Awaitable

    from sqlalchemy.ext.asyncio import AsyncSession

app = typer.Typer()


def version(flag: bool) -> None:
    "print the semantic version"
    if flag:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def callback(
    ctx: typer.Context,
    # config: Path = typer.Option(defaults.config_path),
    database_path: Path = typer.Option(defaults.database_path),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version, is_eager=True
    ),
):
    """
    implements global options for all cli subcommands
    """
    # skip everything if doing cli completion, or there's no subcommand
    if ctx.resilient_parsing or ctx.invoked_subcommand is None:
        return

    from typing import Awaitable

    from sqlalchemy.ext.asyncio import AsyncSession

    from mw_url_shortener.database.start import create_database_file, make_session

    database_path = create_database_file(database_path)

    settings = Settings(database_path=database_path)

    async_session: Awaitable[AsyncSession] = make_session(
        defaults.database_url_leader + str(settings.database_path)
    )

    configure = partial(
        configure_depency_injection, settings=settings, async_session=async_session
    )
    inject.configure(configure)


@app.command()
def show_configuration(json: Optional[bool] = typer.Option(False)) -> None:
    "print the configuration all other subcommands will use"
    settings = inject.instance(Settings)
    if json:
        json_settings = settings.json()
        typer.echo(json_settings)
        return

    settings_data = settings.dict()
    for key in settings_data:
        typer.echo(f"{key}: {settings_data[key]}")


def configure_depency_injection(
    binder: inject.Binder,
    *,
    settings: Settings,
    async_session: "Awaitable[AsyncSession]",
) -> None:
    from typing import Awaitable

    from sqlalchemy.ext.asyncio import AsyncSession

    binder.bind(Settings, settings)
    binder.bind(Awaitable[AsyncSession], async_session)


def main() -> None:
    """
    main entry point
    """
    from mw_url_shortener.cli import user

    app.add_typer(user.app, name="user")
    app()
