"""
settings common to the server and client
"""
import warnings
from pathlib import Path
from string import ascii_lowercase, digits
from typing import Callable, Dict, Optional, Union

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

    def json_dumps(v: Json, *, default: Callable[[Json], str]) -> str:
        """
        orjson.dumps returns bytes, to match standard json.dumps we need to decode

        from:
        https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation
        """
        return orjson.dumps(v, default=default).decode()  # type: ignore


class Defaults(BaseSettings):
    config_path: Path = Path(
        platformdirs.user_config_dir(
            appname=APP_NAME, appauthor=APP_AUTHOR, version=__version__, roaming=True
        )
    )
    # NOTE:FEAT redirects.sqlite should be in a more "typical" location
    database_path: Path = Path("/var/db/redirects.sqlite")
    database_dialect: str = "sqlite"
    database_driver: str = "aiosqlite"
    database_url_scheme: str = f"{database_dialect}+{database_driver}"
    database_url_joiner: str = ":///"
    database_url_leader: str = f"{database_url_scheme}{database_url_joiner}"
    database_url: str = f"{database_url_leader}{database_path}"
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
    redirect_body: Optional[str] = None
    # use a ridiculous number so things break earlier
    # not too ridiculous so the tests don't take too long
    test_string_length: PositiveInt = 100_000

    @validator("database_url_scheme")
    def database_url_scheme_check(
        cls: "Defaults", value: str, values: Dict[str, Union[Path, str]]
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(f"expected str, got '{type(value)}'")

        database_dialect = values["database_dialect"]
        assert isinstance(database_dialect, str)
        database_driver = values["database_driver"]
        assert isinstance(database_driver, str)

        calculated_database_url_scheme = f"{database_dialect}+{database_driver}"

        if not value == calculated_database_url_scheme:
            warnings.warn(
                f"database_url_scheme expected to be {calculated_database_url_scheme!r}, but got {value!r}"
            )

        return calculated_database_url_scheme

    @validator("database_url_leader")
    def database_url_leader_check(
        cls: "Defaults", value: str, values: Dict[str, Union[Path, str]]
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(f"expected str, got '{type(value)}'")

        database_url_scheme = values["database_url_scheme"]
        assert isinstance(database_url_scheme, str)
        database_url_joiner = values["database_url_joiner"]
        assert isinstance(database_url_joiner, str)

        calculated_database_url_leader = f"{database_url_scheme}{database_url_joiner}"

        if not value == calculated_database_url_leader:
            warnings.warn(
                f"database_url_leader expected to be {calculated_database_url_leader!r}, but got {value!r}"
            )

        return calculated_database_url_leader

    @validator("database_url")
    def database_url_check(
        cls: "Defaults", value: str, values: Dict[str, Union[Path, str]]
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(f"expected str, got '{type(value)}'")

        database_url_leader = values["database_url_leader"]
        assert isinstance(database_url_leader, str)
        database_path = values["database_path"]
        assert isinstance(database_path, Path)

        calculated_database_url = f"{database_url_leader}{str(database_path)}"
        if not value == calculated_database_url:
            warnings.warn(
                f"database_url expected to be {calculated_database_url!r}, but got {value!r}"
            )

        return calculated_database_url

    class Config:
        json_loads = json_loads
        json_dumps = json_dumps
        allow_mutation = False


defaults = Defaults()


class Settings(Defaults):
    class Config:
        allow_mutation = True
        env_prefix = APP_NAME.upper() + "__"
        extras = Extra.forbid
