# mypy: allow_any_expr
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import typer

from mw_url_shortener import APP_NAME

from .settings import ServerSettings, inject_server_settings, server_defaults

server_settings_schema = ServerSettings.schema()
server_settings_schema_properties = server_settings_schema["properties"]
database_path_env_names = [
    name.upper()
    for name in server_settings_schema_properties["database_path"]["env_names"]
]
jwt_secret_key_env_names = [
    name.upper()
    for name in server_settings_schema_properties["jwt_secret_key"]["env_names"]
]


def callback(
    ctx: typer.Context,
    database_path: Path = typer.Option(
        server_defaults.database_path, envvar=database_path_env_names
    ),
) -> None:
    # skip everything if doing cli completion, or there's no subcommand
    if ctx.resilient_parsing or ctx.invoked_subcommand is None or "--help" in sys.argv:
        return

    if not database_path.is_file():
        typer.echo(f"expected a file '{database_path}'")
        raise typer.Exit(code=1)

    try:
        from hypercorn.__main__ import main
    except ImportError as err:
        typer.echo(
            f"""were the server extras installed? (pip install {APP_NAME}[server])

cannot import hypercorn: {err}"""
        )
        raise typer.Exit(code=1)

    from functools import partial

    import inject

    # temporary values for missing keys
    server_settings = ServerSettings(jwt_secret_key="", database_path=database_path)
    server_settings_injector = partial(
        inject_server_settings, server_settings=server_settings
    )
    inject.configure(server_settings_injector)


def debug() -> None:
    from subprocess import run
    from unittest.mock import patch

    import inject

    from mw_url_shortener.utils import safe_random_string

    server_settings = inject.instance(ServerSettings)
    database_path: "Path" = server_settings.database_path
    database_path_env_addon = {
        name: str(database_path) for name in database_path_env_names
    }

    jwt_secret_key = safe_random_string(5)
    jwt_secret_key_env_addon = {
        name: str(jwt_secret_key) for name in jwt_secret_key_env_names
    }

    env_patch = {"MAKE_APP": "true"}
    env_patch.update(jwt_secret_key_env_addon)
    env_patch.update(database_path_env_addon)

    with patch.dict("os.environ", env_patch) as patched_env:
        result = run(
            [
                str(sys.executable),
                "-m",
                "hypercorn",
                "mw_url_shortener.server.app:app",
                "--worker-class",
                "uvloop",
                "--access-logfile",
                "-",
                "--error-logfile",
                "-",
                "--debug",
                "--reload",
            ],
            env=patched_env,
            check=False,
        )

    if result.returncode != 0:
        raise typer.Exit(code=result.returncode)


def start(
    ip_address: str = typer.Option(server_defaults.insecure_bind_ip_address),
    port: int = typer.Option(server_defaults.insecure_bind_port),
) -> None:
    raise NotImplementedError


app = typer.Typer(callback=callback)
app.command()(debug)
app.command()(start)
if __name__ == "__main__":
    app()
