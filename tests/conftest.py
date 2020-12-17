"""
pytest fixtures and testing configuration
"""
import os
from pathlib import Path
from random import randint
from typing import Iterable, Tuple
from unittest.mock import patch

import pytest
from pony.orm import Database

from mw_url_shortener.database import get_db, user
from mw_url_shortener.database.interface import setup_db
from mw_url_shortener.settings import CommonSettings
from mw_url_shortener.types import HashedPassword, Username
from mw_url_shortener.utils import random_username
from mw_url_shortener.utils import unsafe_random_chars as random_string
from mw_url_shortener.utils import unsafe_random_hashed_password


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


@pytest.fixture(scope="session")
def random_env_var_names() -> Tuple[str, str]:
    "provide some random environment variables names for each run"
    return (random_string(10).upper(), random_string(11).upper())


@pytest.fixture(scope="function", autouse=True)
def patch_os_environ() -> Iterable[None]:
    """
    patches os.environ so that each test function can modify it to its heart's
    content, and no other test will be able to see those changes
    """
    with patch.dict("os.environ") as nothing:
        yield None
