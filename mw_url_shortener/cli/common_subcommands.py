# mypy: allow_any_expr
import typer

from mw_url_shortener.dependency_injection import get_settings
from mw_url_shortener.settings import FlexibleSettings, OutputStyle, Settings

SHOW_CONFIGURATION_COMMAND_NAME: str = "show-configuration"


def show_configuration() -> None:
    "print the configuration all other subcommands will use"
    settings = get_settings()
    # NOTE:FUTURE serialize property values
    # https://github.com/samuelcolvin/pydantic/issues/935#issuecomment-554378904
    all_settings = FlexibleSettings.parse_obj(
        {
            "database_url": settings.database_url,
            "version": settings.version,
            **settings.dict(),
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
            "test_string_length",
        }
    )
    for key in settings_data:
        typer.echo(f"{key}: {settings_data[key]}")
