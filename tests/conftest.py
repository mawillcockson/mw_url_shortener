"""
pytest fixtures and testing configuration
"""
import os
from pathlib import Path
from random import randint
from typing import Iterable, Tuple
from unittest.mock import _SentinelObject as Sentinel
from unittest.mock import patch, sentinel

import pytest
from pony.orm import Database, db_session

from mw_url_shortener.database import get_db, user
from mw_url_shortener.database.interface import setup_db
from mw_url_shortener.settings import (
    AllowExtraSettings,
    CommonSettings,
    DatabaseSettings,
    SettingsClassName,
)
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
    env_file = (tmp_path / "test.env").resolve()
    return CommonSettings(
        env_file=env_file,
    )


class BadSettings(AllowExtraSettings):
    "a settings class meant to imitate a user-defined class"
    pass


@pytest.fixture
def bad_settings(correct_settings: CommonSettings) -> BadSettings:
    "builds a settings object meant to imitate a correct settings class"
    assert (
        BadSettings not in SettingsClassName._classes
    ), f"{BadSettings} must not be a good settings class"
    bad_settings = BadSettings()
    bad_settings.__class__.__name__ = CommonSettings.__name__
    return bad_settings


@pytest.fixture
def correct_database_settings(
    database: Database, correct_settings: CommonSettings
) -> DatabaseSettings:
    "adds onto correct_settings to return a {DatabaseSettings.__name__}"
    with db_session:
        database_file_name = database.provider.pool.filename
    database_file = Path(database_file_name).resolve(strict=True)
    return DatabaseSettings(**correct_settings.dict(), database_file=database_file)


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


@pytest.fixture(scope="session")
def session_sentinel() -> Sentinel:
    """
    generates a unique object to use as a sentinel value over the course of a
    testing run
    """
    return sentinel.session_sentinel


@pytest.fixture(scope="function", autouse=True)
def patch_os_environ() -> Iterable[None]:
    """
    patches os.environ so that each test function can modify it to its heart's
    content, and no other test will be able to see those changes
    """
    with patch.dict("os.environ", clear=True) as nothing:
        yield None


@pytest.fixture(scope="function", autouse=True)
def clear_settings_cache() -> Iterable[None]:
    """
    patches settings._settings module cache for settings so that each test
    starts with that unset
    """
    with patch("mw_url_shortener.settings._settings", new=None):
        yield None
