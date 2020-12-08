print(f"imported mw_url_shortener.config as {__name__}")
"""
Primarily uses https://github.com/tmbo/questionary
"""
from questionary import Separator, prompt
from enum import Enum
from typing import List, Optional, Union, Callable, NewType
from pathlib import Path
from pydantic import BaseSettings
from argparse import Namespace
from pathlib import Path


class CreateDatabase(str, Enum):
    create = "Create a database"
    use_existing = "Use an existing database (choose file)"

    def __str__(self) -> str:
        """
        from:
        https://www.cosmicpython.com/blog/2020-10-27-i-hate-enums.html
        """
        return str.__str__(self)


first_time_questions = [
    {
        "message": "No database found",
    },
    {
        "message": "Database location",
    },
    {
        "message": "The database already has a user\nAdd user?",
        "choices": [
            "yes",
            "no, I'll add one manually to the SQLite database",
            "no, one already exists",
        ],
    },
    {
        "message": "Generate systemd files?",
        "choices": [
            "user",
            "system",
            "no",
        ],
    },
    {
        "message": """Would you like to put the API behind a hard-to-guess key?
For example:

https://example.com/tgHQiG9o0T/v1/users

Without the key:

https://example.com/v1/users""",
    },
    {
        "message": "Allow unauthenticated local access?",
    },
]

EnvFile = NewType("EnvFile", Union[Path, str, None])

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
    func: Callable[[Namespace], None]
    env_file = EnvFile
    key_length: int = 10

    class Config:
        env_prefix = "url_shortener_"
        orm_mode = True
