"""
the common options and initialization for actions with a local database file,
accessible through the filesystem

the name for this file is intentionally not "local.py" because `local` is a
keyword in Python, and importing it would be cumbersome
"""
import sys
from pathlib import Path

import typer

from mw_url_shortener.database.start import make_sessionmaker
from mw_url_shortener.dependency_injection import (
    reconfigure_dependency_injection,  # this must be imported at the top-level for the run_test_command test fixture
)
from mw_url_shortener.dependency_injection import get_settings
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.interfaces import run_sync
from mw_url_shortener.settings import CliMode, defaults

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
    if (
        ctx.resilient_parsing
        or ctx.invoked_subcommand is None
        or "--help" in sys.argv
        or "--show-completion" in sys.argv
    ):
        return

    settings = get_settings()
    # important, but mainly used in the test suite
    settings.cli_mode = CliMode.local_database
    settings.database_path = database_path
    settings.log_db_access = log_db_access

    if ctx.invoked_subcommand == SHOW_CONFIGURATION_COMMAND_NAME:
        return

    async_sessionmaker = run_sync(
        make_sessionmaker(settings.database_url, echo=log_db_access)
    )

    reconfigure_dependency_injection(
        resource=async_sessionmaker,
        user_interface=database_interface.user,
        redirect_interface=database_interface.redirect,
    )


app = typer.Typer(callback=callback)
app.command(name=SHOW_CONFIGURATION_COMMAND_NAME)(show_configuration)

app.add_typer(user_app, name="user")
app.add_typer(redirect_app, name="redirect")
