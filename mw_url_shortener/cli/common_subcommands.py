import inject
import typer

from mw_url_shortener.settings import OutputStyle, Settings

SHOW_CONFIGURATION_COMMAND_NAME: str = "show-configuration"


def show_configuration() -> None:
    "print the configuration all other subcommands will use"
    settings = inject.instance(Settings)
    if settings.output_style == OutputStyle.json:
        # NOTE:FUTURE serialize property values
        # https://github.com/samuelcolvin/pydantic/issues/935#issuecomment-554378904
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
    settings_data["database_url"] = settings.database_url
    settings_data["version"] = settings.version
    for key in settings_data:
        typer.echo(f"{key}: {settings_data[key]}")
