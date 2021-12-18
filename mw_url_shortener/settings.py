"""
settings common to the server and client
"""
from pathlib import Path
from string import ascii_lowercase, digits
from typing import Optional

import platformdirs
from pydantic import BaseSettings, PositiveInt

from . import APP_AUTHOR, APP_NAME, __version__


class Defaults(BaseSettings):
    # NOTE:FEAT redirects.sqlite should be in a more "typical" location
    config_path: Path = Path(
        platformdirs.user_config_dir(
            appname=APP_NAME, appauthor=APP_AUTHOR, version=__version__, roaming=True
        )
    )
    database_path: Path = Path("/var/db/redirects.sqlite")
    database_url_scheme: str = "sqlite+aiosqlite"
    database_url: str = f"{database_url_scheme}:///{database_path}"
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

    class Config:
        allow_mutation = False


defaults = Defaults()
