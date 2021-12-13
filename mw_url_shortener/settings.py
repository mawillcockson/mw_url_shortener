"""
settings common to the server and client
"""
from pathlib import Path
from typing import Optional

import appdirs
from pydantic import BaseSettings

from . import APP_AUTHOR, APP_NAME, __version__

class Defaults(BaseSettings):
    # NOTE:FEAT redirects.sqlite should be in a more "typical" location
    config_path = Path(
        appdirs.user_config_dir(
            appname=APP_NAME, appauthor=APP_AUTHOR, version=__version__, roaming=True
        )
    )
    database_path = Path("/var/db/redirects.sqlite")
    database_url_scheme = "sqlite+aiosqlite"
    database_url = F"{database_url_scheme}:///{database_path}"
    max_username_length = 30
    max_password_length = 128

    class Config:
        allow_mutation = False


defaults = Defaults()
