"""
server settings
"""
from pathlib import Path
from typing import List, Optional

from pydantic import Extra, NonNegativeInt

from mw_url_shortener.settings import Defaults, Settings


class ServerDefaults(Defaults):
    """
    adapted from hypercorn.config.Config

    More info at:
    https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html#configuration-options
    """

    accesslog: str = "-"  # file location; '-' means stdout
    errorlog: str = "-"  # file location; '-' means stderr
    loglevel: str = "info"
    debug: bool = False
    include_server_header: bool = False
    root_path: str = ""  #
    insecure_bind_ip_address: str = "[::]"
    insecure_bind_port: str = "8080"
    # h11_max_incomplete_size  # the max HTTP/2 request line + headers size in bytes
    # h2_max_concurrent_streams  # maximum number of HTTP/2 concurrent streams
    # h2_max_header_list_size  # maximum number of HTTP/2 headers
    # h2_max_inbound_frame_size  # maximum size of HTTP/2 frame
    use_reloader: bool = False  # enable automatic reloads on code changes
    application_path: Path = Path(".")  # path location of the ASGI application
    backlog: int = 100  # maximum number of pending connections
    graceful_timeout: float = 3.0  # time to wait after SIGTERM or Ctrl-C for any remaining requests (tasks) to complete
    user: Optional[NonNegativeInt] = None  # user to own any Unix sockets
    group: Optional[NonNegativeInt] = None  # group to own any Unix sockets
    server_names: List[
        str
    ] = (
        []
    )  # hostnames that can be served; requests to different hosts will be responded to with 404s


server_defaults = ServerDefaults()


class ServerSettings(ServerDefaults):
    class Config:
        allow_mutation = True
        extra = Extra.forbid
        env_prefix = Settings.Config.env_prefix
