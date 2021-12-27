"the main cli entrypoint"
import asyncio
import sys
from functools import partial
from pathlib import Path
from typing import List, Optional

import inject
import typer

from mw_url_shortener import __version__
from mw_url_shortener.dependency_injection import (
    AsyncLoopType,
    initialize_depency_injection,
    reconfigure_dependency_injection,
)
from mw_url_shortener.settings import OutputStyle, Settings, defaults

from .common_subcommands import show_configuration
from .local_subcommand import app as local_app


def version(flag: bool) -> None:
    "print the semantic version"
    if flag:
        typer.echo(__version__)
        raise typer.Exit()


def callback(
    ctx: typer.Context,
    # config: Path = typer.Option(defaults.config_path),
    output_style: OutputStyle = typer.Option(defaults.output_style.value),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version, is_eager=True
    ),
) -> None:
    """
    implements global options for all cli subcommands
    """
    # skip everything if doing cli completion, or there's no subcommand
    if ctx.resilient_parsing or ctx.invoked_subcommand is None:
        return

    settings = inject.instance(Settings)
    settings.output_style = output_style


app = typer.Typer(callback=callback)
app.command()(show_configuration)
app.add_typer(local_app, name="local")


def main() -> None:
    """
    main entry point
    """

    async def run_typer(app: typer.Typer) -> None:
        initialize_depency_injection()

        return await asyncio.get_running_loop().run_in_executor(None, app)

    asyncio.run(run_typer(app))
