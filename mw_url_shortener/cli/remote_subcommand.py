"""
the common options and initialization for actions with a remote api
"""
import sys

import typer

from mw_url_shortener.dependency_injection import (
    reconfigure_dependency_injection,  # this must be imported at the top-level for the run_test_command test fixture
)
from mw_url_shortener.dependency_injection import get_settings
from mw_url_shortener.interfaces import remote as remote_interface
from mw_url_shortener.remote.start import (
    make_async_client,  # this must be imported at the top-level for the run_test_command test fixture
)
from mw_url_shortener.remote.start import make_async_client_closer
from mw_url_shortener.schemas.user import Password, UserCreate, Username
from mw_url_shortener.settings import CliMode, defaults

from .common_subcommands import SHOW_CONFIGURATION_COMMAND_NAME, show_configuration
from .redirect import app as redirect_app
from .user import app as user_app


def callback(
    ctx: typer.Context,
    base_url: str = typer.Option(
        ...,
        help="the first part of the URL of the API, "
        "or everything before the /openapi.json part "
        "(https://example.org/all/part/of/base/url/openapi.json)",
    ),
    api_prefix: str = typer.Option(
        defaults.api_prefix, help="should match the setting on the server"
    ),
    # NOTE:FEAT it would be nice not to have to enter this if just using --help or --show-completion
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
) -> None:
    if (
        ctx.resilient_parsing
        or ctx.invoked_subcommand is None
        or "--help" in sys.argv
        or "--show-completion" in sys.argv
    ):
        return

    assert UserCreate(
        username=username, password=password
    ), "username and password must be valid"

    settings = get_settings()
    # important, but mainly used in the test suite
    settings.cli_mode = CliMode.remote_api
    settings.base_url = base_url
    settings.api_prefix = api_prefix

    async_client = make_async_client(
        settings, username=Username(username), password=Password(password)
    )

    async_client_closer = make_async_client_closer(async_client)
    ctx.call_on_close(async_client_closer)

    reconfigure_dependency_injection(
        resource=async_client,
        user_interface=remote_interface.user,
        redirect_interface=remote_interface.redirect,
    )


app = typer.Typer(callback=callback)
app.command(name=SHOW_CONFIGURATION_COMMAND_NAME)(show_configuration)

app.add_typer(user_app, name="user")
app.add_typer(redirect_app, name="redirect")
