print(f"imported mw_url_shortener.settings as {__name__}")
from typing import Optional

from pydantic import BaseSettings, Field, Extra

from .types import Key, SPath
from .utils import orjson_dumps, orjson_loads, unsafe_random_chars
from pathlib import Path


class CommonSettings(BaseSettings):
    """
    All of the settings for the application

    The defaults are laid out in this class

    When instantiating, the command-line arguments are passed

    Additionally, environment variables can be set, prefixed with "URL_SHORTENER_",
    or they can be written in a .env file, which is passed as a config file.

    The .env file uses the python-dotenv syntax:
    https://github.com/theskumar/python-dotenv#usages
    """

    env_file: Optional[SPath] = None
    
    class Config:
        env_prefix = "url_shortener_"
        orm_mode = True
        # NOTE: Supposed to help speed up JSON encoding and decoding
        # from:
        # https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation
        json_loads = orjson_loads
        json_dumps = orjson_dumps
        allow_mutation = False
        # Raise errors when extra attributes are passed
        extras = Extra.forbid


class AllowExtraSettings(CommonSettings):
    "purely for adding the config to all subclasses"
    class Config:
        extra = Extra.allow


class DatabaseSettings(AllowExtraSettings):
    database_file: Path


class ClientSettings(AllowExtraSettings):
    api_key: Key


class ServerSettings(ClientSettings, DatabaseSettings):
    # NOTE:BUG The following rules should be eforced:
    # - Does this value have to start with '/'?
    # - Can it end with a '/'?
    # - What characters are allowed?
    # - Does the library to percent-encoding?
    root_path: Optional[str] = None
    reload: bool = False
    key_length: int = 3


_settings: Optional[CommonSettings] = None
