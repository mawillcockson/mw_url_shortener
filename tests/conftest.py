"""
pytest fixtures and testing configuration
"""
from pathlib import Path
from random import randint

import pytest
from pony.orm import Database

from mw_url_shortener.database import get_db, user
from mw_url_shortener.database.interface import setup_db
from mw_url_shortener.settings import CommonSettings
from mw_url_shortener.types import HashedPassword, Username
from mw_url_shortener.utils import (
    random_username,
    unsafe_random_chars,
    unsafe_random_hashed_password,
)


@pytest.fixture
def database(tmp_path: Path) -> Database:
    "makes a database object backed by a real database file"
    return setup_db(
        db=get_db(),
        filename=str((tmp_path / "temp.sqlitedb").resolve()),
        create_tables=True,
    )


@pytest.fixture
def correct_settings(tmp_path: Path, database: Database) -> CommonSettings:
    "makes a complete CommonSettings object, that has realistic values"
    # NOTE:TEST::RANDOMIZATION Best to avoid hardcoded test values where possible
    env_file = (tmp_path / ".env").resolve()
    return CommonSettings(
        env_file=env_file,
        key_length=11,
        api_key=unsafe_random_chars(5),
        root_path=unsafe_random_chars(6),
        database_file=database.provider.pool.filename,
    )
