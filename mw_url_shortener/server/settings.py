# mypy: allow_any_expr
"""
server settings
"""
from datetime import timedelta
from pathlib import Path
from pprint import pformat
from typing import TYPE_CHECKING, List, Optional

from pydantic import AnyUrl, ConstrainedStr, Extra, NonNegativeInt, PositiveInt

from mw_url_shortener import APP_NAME, __version__, metadata
from mw_url_shortener.schemas.base import BaseSchema
from mw_url_shortener.settings import Defaults, Settings
from mw_url_shortener.utils import uppercase_all

if TYPE_CHECKING:
    import inject


class FastAPILicenseInfo(BaseSchema):
    name: str
    url: Optional[str] = None


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
    root_path: str = ""  # https://example.com/{root_path}/{api_prefix}/v0/api/user/me
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
    jwt_hash_algorithm: str = "HS256"
    jwt_access_token_valid_duration: timedelta = timedelta(minutes=30)
    fast_api_title: str = APP_NAME
    fast_api_description: str = metadata["Description"]
    fast_api_version: str = __version__
    fast_api_terms_of_service: Optional[AnyUrl] = None
    fast_api_license_info: FastAPILicenseInfo = FastAPILicenseInfo(
        name="MIT",
        url="https://github.com/mawillcockson/mw_url_shortener/blob/main/LICENSE",
    )
    jwt_secret_key_max_length: PositiveInt = 128
    show_docs: bool = False


server_defaults = ServerDefaults()


class JWTSecretKey(ConstrainedStr):
    max_length = server_defaults.jwt_secret_key_max_length


class ServerSettings(ServerDefaults):
    jwt_secret_key: JWTSecretKey

    class Config:
        allow_mutation = True
        extra = Extra.forbid
        env_prefix = Settings.Config.env_prefix


def inject_server_settings(
    binder: "inject.Binder", *, server_settings: Optional[ServerSettings] = None
) -> None:
    if not server_settings:
        server_settings = ServerSettings()
    binder.bind(ServerSettings, server_settings)


def server_settings_attribute_env_names(attribute_name: str) -> "List[str]":
    server_settings_schema = ServerSettings.schema()
    server_settings_schema_properties = server_settings_schema["properties"]
    if attribute_name not in server_settings_schema_properties:
        raise AttributeError(
            f"cannot find '{attribute_name}' in ServerSettings:\n"
            + pformat(server_settings_schema)
        )
    attribute_schema = server_settings_schema_properties[attribute_name]
    if "env_names" not in attribute_schema or not attribute_schema["env_names"]:
        raise ValueError(
            f"no environment variable names configured for 'ServerSettings.{attribute_name}':\n"
            + pformat(attribute_schema)
        )
    return uppercase_all(attribute_schema["env_names"])
