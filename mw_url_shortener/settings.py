print(f"imported mw_url_shortener.settings as {__name__}")
import enum
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Optional

from pydantic import BaseSettings, Extra, Field, validator

from .types import Key
from .utils import orjson_dumps, orjson_loads, unsafe_random_chars


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

    env_file: Optional[Path] = None

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
    "requires the database_file"
    database_file: Path


class ClientSettings(AllowExtraSettings):
    "requires the api_key"
    api_key: Key


class ServerSettings(ClientSettings, DatabaseSettings):
    "all of the settings needed for starting and running a server"
    # NOTE:BUG The following rules should be eforced:
    # - Does this value have to start with '/'?
    # - Can it end with a '/'?
    # - What characters are allowed?
    # - Does the library to percent-encoding?
    root_path: Optional[str] = None
    reload: bool = False
    key_length: int = 3


_settings: Optional[CommonSettings] = None


SettingsClasses = enum.unique(
    Enum(
        value="SettingsClasses",
        names={
            cls.__name__: cls
            for cls in locals().values()
            if hasattr(cls, "__mro__")
            and issubclass(cls, BaseSettings)
            and cls != BaseSettings
        },
    )
)


class SettingsClassName(str):
    "a name of a settings class from the settings module"
    _class_names = sorted(cls_enum.name for cls_enum in SettingsClasses)

    @classmethod
    def __get_validators__(cls) -> Iterable[Callable[[type, str], "SettingsClassName"]]:
        "returns all the validators"
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> "SettingsClassName":
        "ensures the value matches the requirements and "
        assert (
            value in cls._class_names
        ), f"class name must be a settings class:\n{', '.join(cls._class_names)}"
        return cls(value)

    def __repr__(self) -> str:
        "create a string representation of the value"
        return f"{self.__class__.__name__}({super().__repr__()})"
