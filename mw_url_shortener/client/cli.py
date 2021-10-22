"the main cli entrypoint"
from pathlib import Path
from typing import Optional

import typer

from .. import __version__, settings
from . import user

app = typer.Typer()

app.add_typer(user.app, name="user")


def version(flag: bool) -> None:
    "print the semantic version (the client and server have the same version)"
    if flag:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    local_config: Path = typer.Option(settings.DEFAULT_CONFIG_PATH, "--local"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version, is_eager=True
    ),
):
    """
    implements global options for all client cli subcommands
    """
    # NOTE:FEAT ask for local_config path if not given, offering to use the
    # default path
    if ctx.resilient_parsing:
        return

    if not settings.settings:
        settings.settings = settings.CommonSettings(config_file=local_config)

    ctx.obj = settings.settings

    # NOTE:REMINDER if cleanup should be performed, add a cleanup_function to
    # the context, and use the context as a context manager:
    # ctx.call_on_close(cleanup_function)
    # with ctx as ctx:
