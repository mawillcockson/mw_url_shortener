print(f"imported mw_url_shortener.setup as {__name__}")
"""
Primarily uses https://github.com/tmbo/questionary
"""
from argparse import Namespace
from enum import Enum
from pathlib import Path
from typing import Callable, List, NewType, Optional, Union

from pydantic import BaseSettings, Field
from questionary import Separator, prompt

from .settings import CommonSettings
from .types import Key, SPath
from .utils import orjson_dumps, orjson_loads, unsafe_random_chars


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
