from typing import TYPE_CHECKING

import typer

from mw_url_shortener import APP_NAME

from .settings import server_defaults

if TYPE_CHECKING:
    from asyncio import Event
    from signal import Signals
    from types import FrameType
    from typing import Callable


def callback(ctx: typer.Context) -> None:
    # skip everything if doing cli completion, or there's no subcommand
    if ctx.resilient_parsing or ctx.invoked_subcommand is None:
        return


def make_signal_handler(
    shutdown_event: "Event",
) -> "Callable[[Signals, FrameType], None]":
    def signal_handler(signalnum: "Signals", frame_object: "FrameType") -> None:
        shutdown_event.set()

    return signal_handler


def start(
    ip_address: str = typer.Option(server_defaults.insecure_bind_ip_address),
    port: int = typer.Option(server_defaults.insecure_bind_port),
):
    raise NotImplementedError
    try:
        from hypercorn.config import Config
    except ImportError as err:
        typer.echo(
            f"""were the server extras installed? (pip install {APP_NAME}[server])

cannot import hypercorn: {err}"""
        )
        raise typer.Exit(code=1)

    config = Config()
    config.accesslog = "-"  # stdout
    config.errorlog = "-"  # stderr
    config.loglevel = "info"
    config.include_server_header = False
    # config.root_path =
    config.insecure_bind = f"{ip_address}:{port}"

    import asyncio
    from signal import Signals

    from .routes import app as routes_app

    try:
        import uvicorn

        uvicorn.install()
        config.worker_class = "uvloop"
    except ImportError:
        pass

    shutdown_event = asyncio.Event()

    serve_awaitable = serve(routes_app, config, shutdown_trigger=shutdown_event.wait)

    # import inject

    # if inject.is_configured():
    #     from mw_url_shortener.dependency_injection import AsyncLoopType
    #     from mw_url_shortener.interfaces import run_sync

    #     loop = inject.instance(AsyncLoopType)

    #     async def add_signal_handler_and_serve() -> None:
    #         loop.add_signal_handler(
    #             Signals.SIGTERM, make_signal_handler(shutdown_event)
    #         )
    #         await serve_awaitable

    #     run_sync(add_signal_handler_and_serve())
    # else:

    loop = asyncio.new_event_loop()
    loop.add_signal_handler(Signals.SIGTERM, make_signal_handler(shutdown_event))
    loop.run_until_complete(serve_awaitable)


app = typer.Typer(callback=callback)
app.command()(start)
if __name__ == "__main__":
    app()
