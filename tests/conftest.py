"""
pytest fixtures and testing configuration
"""
import os
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
    )


@pytest.fixture(autouse=True)
def remove_settings_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    can't guarantee that the settings won't pull environment variables from the
    test environment, since pydantic provides a lot of ways of setting the
    names of environment variables it should in for values, but any current
    environment variables that have the same prefix as what the settings class
    will be looking for can be made unavailable to the function under test:
    """
    env_prefix: str = CommonSettings.Config().env_prefix
    for env_var_name in os.environ:
        if env_var_name.startswith(env_prefix):
            monkeypatch.delenv(env_var_name)
