"""
settings common to the server and client
"""
import warnings
from enum import Enum
from pathlib import Path
from string import ascii_lowercase, digits
from typing import Callable, Dict, List, Optional

import platformdirs
from pydantic import BaseSettings, Extra, Json, PositiveInt, validator

from . import APP_AUTHOR, APP_NAME, __version__

try:
    import orjson
except ImportError:
    import json

    json_loads = json.loads  # type: ignore
    json_dumps = json.dumps  # type: ignore
else:
    json_loads = orjson.loads  # type: ignore

    def json_dumps(v: Json, *, default: Callable[[Json], str], indent: Optional[int] = None) -> str:  # type: ignore
        """
        orjson.dumps returns bytes, to match standard json.dumps we need to decode

        from:
        https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation
        """
        if indent:
            return orjson.dumps(v, default=default, option=orjson.OPT_INDENT_2).decode()
        return orjson.dumps(v, default=default).decode()


class OutputStyle(Enum):
    "styles in which to print configuration"
    json = "json"
    text = "text"
    # ini = "ini"


class CliMode(Enum):
    "whether the cli interacts with a local database, or a remote API"
    local_database = "local_database"
    remote_api = "remote_api"


class Defaults(BaseSettings):
    config_dir: Path = Path(
        platformdirs.user_config_dir(
            appname=APP_NAME, appauthor=APP_AUTHOR, version=__version__, roaming=True
        )
    )
    config_path: Path = config_dir / "config.json"
    # NOTE:FEAT redirects.sqlite should be in a more "typical" location
    database_path: Path = Path("/var/db/redirects.sqlite")
    database_dialect: str = "sqlite"
    database_driver: str = "aiosqlite"
    database_url_joiner: str = ":///"
    max_username_length: PositiveInt = 30
    max_password_length: PositiveInt = 128
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#redirection_messages
    # 307 indicates the User Agent (browser) must not change the request method
    redirect_response_status: PositiveInt = 307
    redirect_url: str = "https://google.com"
    redirect_case_sensitive: bool = False
    short_link_characters: str = ascii_lowercase + digits
    # this website lists the formulae for different types of combinations and
    # permutations:
    # https://www.mathsisfun.com/combinatorics/combinations-permutations-calculator.html
    # with the 36 letters and digits, there are 1_679_616 unique permutations
    # of length 4, and 46_656 unique permutations of length 3
    short_link_length: PositiveInt = 4
    redirect_body: str = ""
    output_style: OutputStyle = OutputStyle.text
    cli_mode: Optional[CliMode] = None
    log_db_access: bool = False
    oauth2_endpoint: str = "token"

    @property
    def database_url_scheme(self) -> str:
        return f"{self.database_dialect}+{self.database_driver}"

    @property
    def database_url_leader(self) -> str:
        return f"{self.database_url_scheme}{self.database_url_joiner}"

    @property
    def database_url(self) -> str:
        return f"{self.database_url_leader}{self.database_path}"

    @property
    def version(self) -> str:
        "app version should not be modifiable"
        return __version__

    class Config:
        json_loads = json_loads  # type: ignore
        json_dumps = json_dumps  # type: ignore
        allow_mutation = False

        # prevents pulling in environment variables with the same name as properties
        env_prefix = APP_NAME.upper() + "__DEFAULT__"


defaults = Defaults()


class Settings(Defaults):
    class Config:
        allow_mutation = True
        extra = Extra.forbid
        env_prefix = APP_NAME.upper() + "__"


class FlexibleSettings(Settings):
    class Config:
        extra = Extra.allow
