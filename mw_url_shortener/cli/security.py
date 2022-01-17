from datetime import datetime

import typer
from pydantic import ValidationError, parse_raw_as

from mw_url_shortener.dependency_injection import get_settings
from mw_url_shortener.schemas.user import Username, UserUpdate
from mw_url_shortener.security import make_jwt_token
from mw_url_shortener.server.settings import (
    server_defaults,
    server_settings_attribute_env_names,
)
from mw_url_shortener.settings import OutputStyle
from mw_url_shortener.utils import uppercase_all

jwt_secret_key_env_names = server_settings_attribute_env_names("jwt_secret_key")
jwt_hash_algorithm_env_names = server_settings_attribute_env_names("jwt_hash_algorithm")


def make_token(
    username: str = typer.Option(
        ...,
        help=f"""username of user in the api's database;
must be between {Username.min_length} and {Username.max_length},
inclusive""",
    ),
    token_expiration: str = typer.Option(
        ...,
        help="the date and time the token should expire at, "
        "in ISO 8601 format (e.g. yyyy-mm-ddThh:mm[:ss])",
    ),
    jwt_secret_key: str = typer.Option(
        ...,
        help="set this to the same jwt_secret_key as in the "
        "server configuration to produce tokens the server will accept as valid",
        envvar=jwt_secret_key_env_names,
    ),
    algorithm: str = typer.Option(
        server_defaults.jwt_hash_algorithm,
        help="set this to the same jwt_secret_key as in the server "
        "configuration to produce tokens the server will accept as valid",
        envvar=jwt_hash_algorithm_env_names,
    ),
) -> None:
    """
    prints a jwt token that may be able to be used to authenticate with the api
    """
    settings = get_settings()
    try:
        UserUpdate(username=username)
    except ValidationError as error:
        if settings.output_style == OutputStyle.text:
            typer.echo("bad username")
        raise typer.Exit(code=1) from error

    try:
        # normally, this parse JSON, so the string can be wrapped in double
        # quotes to simulate a JSON string
        expiration_datetime = parse_raw_as(datetime, f'"{token_expiration!s}"')
    except ValidationError as error:
        if settings.output_style == OutputStyle.text:
            typer.echo(f"cannot parse the token expiration '{token_expiration}'")
        raise typer.Exit(code=1) from error

    if not username:
        raise typer.Exit(code=1)

    access_token = make_jwt_token(
        username=username,
        token_expiration=expiration_datetime,
        jwt_secret_key=jwt_secret_key,
        algorithm=algorithm,
    )

    typer.echo(access_token.access_token)


app = typer.Typer()
app.command()(make_token)
