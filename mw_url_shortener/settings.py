"""
settings common to the server and client
"""
from pathlib import Path
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

    class Config:
        allow_mutation = False


defaults = Defaults()
