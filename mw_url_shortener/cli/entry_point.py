"the main cli entrypoint"
import asyncio
import sys
from enum import Enum
from functools import partial
from pathlib import Path
from typing import List, Optional

import inject
import typer

from mw_url_shortener import __version__
from mw_url_shortener.settings import Settings, defaults

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

    settings = Settings(database_path=database_path)

    configure = partial(configure_depency_injection, settings=settings)
    inject.configure(configure)


class Style(Enum):
    "styles in which to print configuration"
    json = "json"
    text = "text"
    # ini = "ini"


# should output style be a global option, so that the tests can use pydantic
# schemas to verify everything's working, or should the verification be done by
# calling another command (e.g. checking a user can be created by first
# creating that user, then searching for the user)
#
# I think it would be better to have a global option
#
# should error information be json-encoded?
# yes, once the API and remote client are written, errors will be returned
# partially as json anyways, I think, so the schemas used can be returned as
# json
#
# at some point I'd like to support being able to show the configuration in
# ini-style, since that's what could be used in a configuration file
#
# this would make it hard to to a global output-style option, as ini-style
# would really only be used for show-configuration
#
# alternatively, ini-configs could be dropped, and the config file format could
# be just json
#
# editing this by hand wouldn't be the most fun, but if there's parity between
# command-line configuration (e.g. passing global configuration options) and
# file configuration, then it would be possible to pipe the output of
# show-configuration in json mode to a file, and changing configuration would
# be as simple as passing that configuration option, and piping to a file again
#
# a save-configuration command could be added to save people from having to do
# the piping themselves
@app.command()
def show_configuration(style: Style = typer.Option("text")) -> None:
    "print the configuration all other subcommands will use"
    settings = inject.instance(Settings)
    if style == Style.json:
        json_settings = settings.json()
        typer.echo(json_settings)
        return

    settings_data = settings.dict(
        exclude={
            "database_dialect",
            "database_driver",
            "database_url_scheme",
            "database_url_joiner",
            "database_url_leader",
            "test_string_length",
        }
    )
    for key in settings_data:
        typer.echo(f"{key}: {settings_data[key]}")


def configure_depency_injection(
    binder: inject.Binder,
    *,
    settings: Settings,
    configurators: List[inject.BinderCallable] = [],
) -> None:
    for configurator in configurators:
        binder.install(configurator)
    binder.bind(Settings, settings)


def main() -> None:
    """
    main entry point
    """
    from mw_url_shortener.cli import user

    app.add_typer(user.app, name="user")

    async def run_typer(app: typer.Typer) -> None:
        return app()

    asyncio.run(run_typer(app))
