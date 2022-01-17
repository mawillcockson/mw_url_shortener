# mypy: allow_any_expr
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import typer

from mw_url_shortener import APP_NAME

from .settings import server_defaults, server_settings_attribute_env_names

if TYPE_CHECKING:
    from typing import Dict, Iterable, List

    EnvPatch = Dict[str, str]


def make_env_patch(names: "Iterable[str]", value: str) -> "EnvPatch":
    return {name: value for name in names}


database_path_env_names = server_settings_attribute_env_names("database_path")
jwt_secret_key_env_names = server_settings_attribute_env_names("jwt_secret_key")
show_docs_env_names = server_settings_attribute_env_names("show_docs")


def callback(
    ctx: typer.Context,
    jwt_secret_key: str = typer.Option(..., envvar=jwt_secret_key_env_names),
    database_path: Path = typer.Option(
        server_defaults.database_path, envvar=database_path_env_names
    ),
    show_docs: bool = typer.Option(
        server_defaults.show_docs,
        envvar=show_docs_env_names,
        help="if passed, api documentation is generated and available (ignored by debug command)",
    ),
) -> None:
    # skip everything if doing cli completion, or there's no subcommand
    if (
        ctx.resilient_parsing
        or ctx.invoked_subcommand is None
        or "--help" in sys.argv
        or "--show-completion" in sys.argv
    ):
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

    from .settings import ServerSettings

    server_settings = ServerSettings(
        jwt_secret_key=jwt_secret_key, database_path=database_path, show_docs=show_docs
    )

    env_patch: "EnvPatch" = {"MAKE_APP": "true"}

    database_path_env_addon = make_env_patch(
        database_path_env_names, str(database_path)
    )
    env_patch.update(database_path_env_addon)

    jwt_secret_key_env_addon = make_env_patch(
        jwt_secret_key_env_names, str(jwt_secret_key)
    )
    env_patch.update(jwt_secret_key_env_addon)

    if show_docs:
        show_docs_env_addon = make_env_patch(show_docs_env_names, "true")
        env_patch.update(show_docs_env_addon)

    import inject

    def config(binder: "inject.Binder") -> None:
        binder.bind("EnvPatch", env_patch)

    inject.configure(config)


def debug() -> None:
    from subprocess import run
    from typing import cast
    from unittest.mock import patch

    import inject

    env_patch = cast("EnvPatch", inject.instance("EnvPatch"))

    # always turn documentation on
    show_docs_env_addon = make_env_patch(show_docs_env_names, "true")
    env_patch.update(show_docs_env_addon)

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
                "--log-level",
                "debug",
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
