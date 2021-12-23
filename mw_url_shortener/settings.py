"""
settings common to the server and client
"""
from pathlib import Path
from string import ascii_lowercase, digits
from typing import Callable, Optional

import platformdirs
from pydantic import BaseSettings, Extra, Json, PositiveInt

from . import APP_AUTHOR, APP_NAME, __version__


class Defaults(BaseSettings):
    # NOTE:FEAT redirects.sqlite should be in a more "typical" location
    config_path: Path = Path(
        platformdirs.user_config_dir(
            appname=APP_NAME, appauthor=APP_AUTHOR, version=__version__, roaming=True
        )
    )
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

    class Config:
        try:
            import orjson
        except ImportError:
            import json

            json_loads = json.loads
            json_dumps = json.dumps
        else:
            json_loads = orjson.loads

            def orjson_dumps(v: Json, *, default: Callable[[Json], str]):
                """
                orjson.dumps returns bytes, to match standard json.dumps we need to decode

                from:
                https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation
                """
                return orjson.dumps(v, default=default).decode()

        allow_mutation = False


defaults = Defaults()


class Settings(Defaults):
    class Config:
        allow_mutation = True
        env_prefix = APP_NAME.upper() + "__"
        extras = Extra.forbid
