from pathlib import Path
from typing import TYPE_CHECKING

import typer

from mw_url_shortener import APP_NAME

from .settings import ServerSettings, inject_server_settings, server_defaults

if TYPE_CHECKING:
    from asyncio import Event
    from types import FrameType
    from typing import Callable, Optional

    from fastapi import FastAPI


def make_fastapi_app(server_settings: ServerSettings) -> "FastAPI":
    from functools import partial

    import inject

    from mw_url_shortener.interfaces import install_binder_callables

    server_settings_injector = partial(
        inject_server_settings, server_settings=server_settings
    )

    configurators = [
        server_settings_injector,
    ]

    injector = partial(install_binder_callables, configurators=configurators)

    inject.configure(injector)

    from fastapi import FastAPI

    from .routes.dependencies.security import oauth2_scheme
    from .routes.v0 import api_router as api_router_v0
    from .routes.v0.redirect import match_redirect
    from .routes.v0.security import login_for_access_token
    from .routes.v0.security import router as api_router_v0_security

    oauth2_scheme.model.flows.password.tokenUrl = str(server_settings.oauth2_endpoint)  # type: ignore

    api_router_v0_security.post(f"/{server_settings.oauth2_endpoint}")(
        login_for_access_token
    )

    app = FastAPI()
    app.include_router(api_router_v0, prefix="/v0")
    app.post(f"/{server_settings.oauth2_endpoint}")(login_for_access_token)
    # this must come last so it doesn't overwrite anything
    app.get("/{short_link:path}")(match_redirect)

    return app


def callback(ctx: typer.Context) -> None:
    # skip everything if doing cli completion, or there's no subcommand
    if ctx.resilient_parsing or ctx.invoked_subcommand is None:
        return


def make_signal_handler(
    shutdown_event: "Event",
) -> "Callable[[int, Optional[FrameType]], None]":
    def signal_handler(
        signalnum: "Optional[int]" = None, frame_object: "Optional[FrameType]" = None
    ) -> None:
        shutdown_event.set()

    return signal_handler


def debug(database_path: Path = typer.Option(...)) -> None:
    if not database_path.is_file():
        typer.echo(f"expected a file '{database_path}'")
        raise typer.Exit(code=1)

    try:
        from hypercorn.config import Config
    except ImportError as err:
        typer.echo(
            f"""were the server extras installed? (pip install {APP_NAME}[server])

cannot import hypercorn: {err}"""
        )
        raise typer.Exit(code=1)

    config = Config()
    config.accesslog = "-"
    config.errorlog = "-"

    from mw_url_shortener.utils import safe_random_string

    jwt_secret_key = safe_random_string(5)

    server_settings = ServerSettings(
        database_path=database_path,
        jwt_secret_key=jwt_secret_key,
        accesslog="-",
        errorlog="-",
    )

    typer.echo(f"server_settings: {server_settings.json(indent=2)}")

    server_app = make_fastapi_app(server_settings)

    # from:
    # https://gitlab.com/pgjones/hypercorn/-/blob/73733d71b804e49a14926633132eef7d54075578/src/hypercorn/asyncio/run.py#L62-73

    import asyncio
    import signal

    shutdown_event = asyncio.Event()
    signal_handler = make_signal_handler(shutdown_event)
    loop = asyncio.new_event_loop()

    for signal_name in {"SIGINT", "SIGTERM", "SIGBREAK"}:
        if hasattr(signal, signal_name):
            try:
                loop.add_signal_handler(getattr(signal, signal_name), signal_handler)
            except NotImplementedError:
                # Add signal handler may not be implemented on Windows
                signal.signal(getattr(signal, signal_name), signal_handler)

    from hypercorn.asyncio import serve

    serve_awaitable = serve(server_app, config, shutdown_trigger=shutdown_event.wait)
    loop.run_until_complete(serve_awaitable)


def start(
    ip_address: str = typer.Option(server_defaults.insecure_bind_ip_address),
    port: int = typer.Option(server_defaults.insecure_bind_port),
) -> None:
    raise NotImplementedError


#     try:
#         from hypercorn.config import Config
#     except ImportError as err:
#         typer.echo(
#             f"""were the server extras installed? (pip install {APP_NAME}[server])
#
# cannot import hypercorn: {err}"""
#         )
#         raise typer.Exit(code=1)
#
#     config = Config()
#     config.accesslog = "-"  # stdout
#     config.errorlog = "-"  # stderr
#     config.loglevel = "info"
#     config.include_server_header = False
#     # config.root_path =
#     config.insecure_bind = f"{ip_address}:{port}"
#
#     import asyncio
#     from signal import Signals
#
#     from .routes import app as routes_app
#
#     try:
#         import uvloop
#
#         uvloop.install()
#         config.worker_class = "uvloop"
#     except ImportError:
#         pass
#
#     shutdown_event = asyncio.Event()
#
#     serve_awaitable = serve(routes_app, config, shutdown_trigger=shutdown_event.wait)
#
#     # import inject
#
#     # if inject.is_configured():
#     #     from mw_url_shortener.dependency_injection import AsyncLoopType
#     #     from mw_url_shortener.interfaces import run_sync
#
#     #     loop = inject.instance(AsyncLoopType)
#
#     #     async def add_signal_handler_and_serve() -> None:
#     #         loop.add_signal_handler(
#     #             Signals.SIGTERM, make_signal_handler(shutdown_event)
#     #         )
#     #         await serve_awaitable
#
#     #     run_sync(add_signal_handler_and_serve())
#     # else:
#
#     loop = asyncio.new_event_loop()
#     loop.add_signal_handler(Signals.SIGTERM, make_signal_handler(shutdown_event))
#     loop.run_until_complete(serve_awaitable)


app = typer.Typer(callback=callback)
app.command()(debug)
app.command()(start)
if __name__ == "__main__":
    app()
