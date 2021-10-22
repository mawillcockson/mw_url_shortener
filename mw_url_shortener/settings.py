"""
settings common to the server and client
"""
from pathlib import Path
from typing import Optional

import appdirs
from pydantic import BaseSettings, root_validator

from . import APP_AUTHOR, APP_NAME, __version__

# NOTE:FEAT redirects.sqlite should be in a more "typical" location
DEFAULT_DATABASE_PATH = Path("/var/db/redirects.sqlite")
DEFAULT_CONFIG_PATH = Path(
    appdirs.user_config_dir(
        appname=APP_NAME, appauthor=APP_AUTHOR, version=__version__, roaming=True
    )
)
DEFAULT_DATABASE_URL_SCHEME = "sqlite+aiosqlite"
DEFAULT_DATABASE_URL = f"{DEFAULT_DATABASE_URL_SCHEME}:///{DEFAULT_DATABASE_PATH}"


class CommonSettings(BaseSettings):
    config_file: Path = DEFAULT_CONFIG_PATH
    database_url: str = DEFAULT_DATABASE_URL


settings: Optional[CommonSettings] = None
