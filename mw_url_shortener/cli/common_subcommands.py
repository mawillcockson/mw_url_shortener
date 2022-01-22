# mypy: allow_any_expr
from typing import TYPE_CHECKING

import inject
import typer

from mw_url_shortener.dependency_injection.remote_interface import get_async_client
from mw_url_shortener.dependency_injection.settings import get_settings
from mw_url_shortener.remote.authentication import OAuth2PasswordBearerHandler
from mw_url_shortener.settings import CliMode, FlexibleSettings, OutputStyle, Settings

SHOW_CONFIGURATION_COMMAND_NAME: str = "show-configuration"
if TYPE_CHECKING:
    from typing import Dict


def show_configuration() -> None:
    "print the configuration all other subcommands will use"
    settings = get_settings()

    additional_settings: "Dict[str, str]" = {}
    if settings.base_url is not None:
        additional_settings["api_base_url"] = settings.api_base_url

    try:
        async_client = get_async_client()
    except (inject.ConstructorTypeError, inject.InjectorException) as error:
        # maybe called from the main command group and async_client wasn't
        # configured
        pass
    else:
        auth = async_client.auth
        assert isinstance(
            auth, OAuth2PasswordBearerHandler
        ), "async_client was created without OAuth2PasswordBearerHandler"

        username = auth.username
        if username is not None:
            additional_settings["username"] = username

        password = auth.password
        if password is not None:
            additional_settings["password"] = password

        token = auth.token
        if token is not None:
            additional_settings["token"] = token

    # NOTE:FUTURE serialize property values
    # https://github.com/samuelcolvin/pydantic/issues/935#issuecomment-554378904
    all_settings = FlexibleSettings.parse_obj(
        {
            **settings.dict(),
            "database_url_scheme": settings.database_url_scheme,
            "database_url_leader": settings.database_url_leader,
            "database_url": settings.database_url,
            "version": settings.version,
            **additional_settings,
        }
    )

    if settings.output_style == OutputStyle.json:
        json_settings = all_settings.json()
        typer.echo(json_settings)
        return

    settings_data = all_settings.dict(
        exclude={
            "database_dialect",
            "database_driver",
            "database_url_scheme",
            "database_url_joiner",
            "database_url_leader",
            "cli_mode",
        }
    )
    for key in settings_data:
        typer.echo(f"{key}: {settings_data[key]}")
