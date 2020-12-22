"""
ensures mw_url_shortener.config behaves correctly
"""
import os
from pathlib import Path
from typing import Dict, NamedTuple, Tuple, Union

import pytest
from pony.orm import Database
from pydantic import ValidationError

from mw_url_shortener import config, settings
from mw_url_shortener.config import (
    CacheConfigError,
    CacheConfigTypeError,
    ConfigError,
    ConfigTypeError,
    EnvConfigError,
    EnvConfigTypeError,
    Namespace,
)
from mw_url_shortener.settings import (
    AllowExtraSettings,
    CommonSettings,
    DatabaseSettings,
    SettingsClassName,
    SettingsTypeError,
)


def test_get_module_cache(correct_settings: CommonSettings) -> None:
    "if the modue cache is already set, can those settings be retrieved"
    settings._settings = correct_settings
    assert config.get_module_cache() == correct_settings
    # Ensure calling the function didn't modify the cache
    assert settings._settings == correct_settings


def test_get_module_cache_bad_type() -> None:
    """
    is an error raised if the module cache is populated with a bad settings
    object
    """

    class BadClass(AllowExtraSettings):
        "a class meant to simulate a user-defined class"
        database_file: Path = Path("example.sqlitedb")

    bad_settings = BadClass()
    bad_settings.__class__.__name__ = DatabaseSettings.__name__
    settings._settings = bad_settings

    with pytest.raises(CacheConfigTypeError) as err:
        config.get_module_cache()
    assert (
        f"settings type in cache not one of ({', '.join(SettingsClassName._class_names)})"
        in str(err.value)
    )


def test_set_module_cache_different_type(
    correct_settings: CommonSettings, correct_database_settings: DatabaseSettings
) -> None:
    """
    is an error raised if the module cache is already set with a different
    settings class
    """
    settings._settings = correct_settings

    with pytest.raises(CacheConfigTypeError) as err:
        config.set_module_cache(new_settings=correct_database_settings)
    assert (
        "cache type does not match new_settings type: "
        f"'{correct_settings.__class__.__name__}' vs "
        f"'{correct_database_settings.__class__.__name__}'"
    ) in str(err.value)


def test_set_get_module_cache(correct_settings: CommonSettings) -> None:
    "can the module cache be set and retrieved"
    assert settings._settings is None

    config.set_module_cache(new_settings=correct_settings)

    assert config.get_module_cache() == correct_settings
    assert settings._settings == correct_settings


@pytest.mark.xfail  # NOTE:NEXT
def test_get_updates_env(correct_settings: CommonSettings) -> None:
    "is the environment updated"
    assert list(os.environ) == ["PYTEST_CURRENT_TEST"]
    settings._settings = correct_settings
    env_names = config.settings_env_names()
    class_name = env_names.class_name
    value_name = env_names.value_name

    returned_settings = config.get()
    assert returned_settings == correct_settings
    assert os.getenv(class_name, None) == type(correct_settings).__name__
    assert os.getenv(value_name, None) == correct_settings.json()


@pytest.mark.xfail  # NOTE:NEXT
def test_get_updates_everwhere(
    database: Database, correct_database_settings: DatabaseSettings
) -> None:
    "is the environment, database, and cache all updated to match"
    # Show that there's no configuration in the database
    with pytest.raises(ValueError) as err:
        config.get_from_db(db=database)
    # Show that there's no configuration in the environment
    env_names = config.settings_env_names()
    class_name = env_names.class_name
    value_name = env_names.value_name
    assert os.getenv(class_name, None) is None
    assert os.getenv(value_name, None) is None
    # Put the configuration in the module cache
    settings._settings = correct_database_settings

    # Use config.get()
    returned_settings = config.get()
    # Ensure the module cache is still the same
    assert settings._settings == correct_database_settings
    # Check that the returned settings match the module cache
    assert returned_settings == correct_database_settings
    # Verify the environment got the settings
    assert os.getenv(class_name, None) == type(correct_database_settings).__name__
    assert os.getenv(value_name, None) == correct_database_settings.json()
    # Verify the database was updated
    assert config.get_from_db(db=database) == correct_database_settings


@pytest.mark.xfail  # NOTE:NEXT
def test_save_sets_everywhere(
    database: Database, correct_database_settings: DatabaseSettings
) -> None:
    "is the environment, database, and cache all updated to match"
    # Show that the cache is empty
    assert settings._settings is None
    # Show the database is empty
    with pytest.raises(ValueError):
        config.get_from_db(db=database)
    # Show the environment is unset, except for pytest's marker
    assert list(os.environ) == ["PYTEST_CURRENT_TEST"]

    # Save the configuration
    config.save(new_settings=correct_database_settings)
    # Grab the settings from the database
    settings_in_db = config.get_from_db(db=database)
    # Grab the settings from the environment
    settings_in_env = config.get_env()
    # Show that the cache is updated
    assert settings._settings == correct_database_settings
    # Show that the environment was updated
    assert settings_in_env == correct_database_settings
    # Show that the database was updated
    assert settings_in_db == correct_database_settings


@pytest.mark.xfail  # NOTE:NEXT
def test_save_allow_bad_db(
    tmp_path: Path, correct_database_settings: DatabaseSettings
) -> None:
    """
    will updating the database be skipped if the database file points to a bad
    database
    """
    assert settings._settings is None
    assert list(os.environ) == ["PYTEST_CURRENT_TEST"]
    nonexistent_database_file = tmp_path / "nonexistent.sqlitedb"
    # Fill the database with nonsense
    nonexistent_database_file.write_bytes(bytes(range(256)))
    assert bad_database_file.is_file()
    bad_database_file_settings = correct_database_settings.copy(
        update={"database_file": bad_database_file}
    )

    config.save(new_settings=bad_database_file_settings)
    settings_in_env = config.get_env()
    assert settings._settings == bad_database_file_settings
    assert settings_in_env == bad_database_file_settings
    # Show that the database hasn't been modified
    assert bad_database_file.read_bytes() == bytes(range(256))


@pytest.mark.xfail  # NOTE:NEXT
def test_save_allow_nonexistent_db(
    tmp_path: Path, correct_database_settings: DatabaseSettings
) -> None:
    """
    will updating the database be skipped if the database file points to a bad
    database
    """
    assert settings._settings is None
    assert list(os.environ) == ["PYTEST_CURRENT_TEST"]
    nonexistent_database_file = tmp_path / "nonexistent.sqlitedb"
    assert not nonexistent_database_file.exists()
    nonexistent_database_file_settings = correct_database_settings.copy(
        update={"database_file": nonexistent_database_file}
    )

    config.save(new_settings=bad_database_file_settings)
    settings_in_env = config.get_env()
    assert settings._settings == nonexistent_database_file_settings
    assert settings_in_env == nonexistent_database_file_settings
    assert not nonexistent_database_file.exists()


@pytest.mark.xfail  # NOTE:NEXT
def test_get_priorities(correct_database_settings: DatabaseSettings) -> None:
    """
    is the priority of the sources for configuration information:
    defaults < dotenv < env vars < database < args
    """

    class ExtraProperties(AllowExtraSettings):
        "adds extra properties used for this test"
        example: int = 5
        demo: set = {0, 1, 2}

    default_settings = ExtraProperties(env_file=None)


@pytest.mark.xfail
def test_from_db() -> None:
    "config.from_db()"
    raise NotImplementedError


@pytest.mark.xfail
def test_to_db() -> None:
    "config.to_db()"
    raise NotImplementedError


@pytest.mark.xfail
def test_save() -> None:
    "config.save()"
    raise NotImplementedError


@pytest.mark.xfail  # NOTE:NEXT
def test_json(correct_settings: CommonSettings) -> None:
    """
    does config.json() produce the same output as the .json() method on
    BaseSettings objects
    """
    config.save(new_settings=correct_settings)

    assert config.json() == correct_settings.json()


@pytest.mark.xfail  # NOTE:NEXT
def test_write_dotenv_no_args(
    database: Database, correct_database_settings: DatabaseSettings
) -> None:
    """
    when called with no arguments, does config.write_dotenv() write out an
    environment file to the env_file in the current settings, using the
    currently set settings
    """
    env_file = correct_database_settings.env_file
    assert isinstance(env_file, Path)
    assert envfile.is_file()
    assert env_file.read_text() == ""
    env_names = config.settings_env_names()

    config.save(new_settings=correct_database_settings)
    # Write the settings to the env_file in the settings
    config.write_dotenv()
    # Delete settings from the database
    with db_session:
        database.ConfigEntity["current"].delete()
        database.commit()
    # Delete settings from the environment
    del os.environ[env_names.class_name]
    del os.environ[env_names.value_name]
    # Clear the settings module cache
    settings._settings = None

    # Instantiate the settings using only the env_file
    settings_from_env_file = DatabaseSettings(
        _env_file=correct_database_settings.env_file
    )
    assert settings_from_env_file == correct_database_settings


@pytest.mark.xfail  # NOTE:NEXT
def test_write_dotenv_no_args_no_settings() -> None:
    """
    is an error raised when config.write_dotenv() is called without arguments
    and without any settings set
    """
    with pytest.raises(ValueError) as err:
        config.write_dotenv()
    assert "need an env_file" in str(err.value)


@pytest.mark.xfail  # NOTE:NEXT
def test_write_dotenv_just_env_file(
    correct_database_settings: DatabaseSettings, database: Database
) -> None:
    """
    does config.write_dotenv() raise an error when it's called with just an
    env_file, and settings aren't set
    """
    # Show that the database doesn't have settings
    with pytest.raises(ValueError):
        config.get_from_db(db=database)
    # Show that the environment is empty
    env_names = config.settings_env_names()
    assert os.getenv(env_names.class_name, None) is None
    assert os.getenv(env_names.value_name, None) is None
    # Show that the settings module cache is unset
    assert settings._settings is None
    # Show that the env_file exists and is empty
    env_file = correct_database_settings.env_file
    assert isinstance(env_file, Path)
    assert envfile.is_file()
    assert env_file.read_text() == ""

    with pytest.raises(ValueError) as err:
        config.write_dotenv(env_file=env_file)
    assert "no settings found" in str(err.value)

    # Show that the database didn't have settings added
    with pytest.raises(ValueError):
        config.get_from_db(db=database)
    # Show that the environment is unmodified
    assert os.getenv(env_names.class_name, None) is None
    assert os.getenv(env_names.value_name, None) is None
    # Show the settings module cache is still unset
    assert settings._settings is None


@pytest.mark.xfail  # NOTE:NEXT
def test_write_dotenv(
    database: Database, correct_database_settings: DatabaseSettings
) -> None:
    """
    if called with all parameters filled, does config.write_dotenv() write out
    an env_file without expecting any settings to be set, and without setting
    any settings
    """
    # Show that the environment file exists and is empty
    env_file = correct_database_settings.env_file
    assert isinstance(env_file, Path)
    assert envfile.is_file()
    assert env_file.read_text() == ""

    # Show that the database doesn't have settings
    with pytest.raises(ValueError):
        config.get_from_db(db=database)
    # Show that the environment is empty
    env_names = config.settings_env_names()
    assert os.getenv(env_names.class_name, None) is None
    assert os.getenv(env_names.value_name, None) is None
    # Show that the settings module cache is unset
    assert settings._settings is None

    # Write the settings to the env_file
    config.write_dotenv(
        filename=correct_database_settings.env_file,
        configuration=correct_database_settings,
    )

    # Show that the database didn't have settings added
    with pytest.raises(ValueError):
        config.get_from_db(db=database)
    # Show that the environment is unmodified
    assert os.getenv(env_names.class_name, None) is None
    assert os.getenv(env_names.value_name, None) is None
    # Show the settings module cache is still unset
    assert settings._settings is None

    # Instantiate the settings using only the env_file
    settings_from_env_file = DatabaseSettings(
        _env_file=correct_database_settings.env_file
    )
    assert settings_from_env_file == correct_database_settings


@pytest.mark.xfail
def test_get_read_only_env_file() -> None:
    """
    can config.get() function if the env_file is on a read-only filesystem
    """
    raise NotImplementedError


@pytest.mark.xfail
def test_write_dotenv_matching_read_only_env_file() -> None:
    """
    does config.write_dotenv() silently succeed when the env_file is read-only,
    but already holds everything it should
    """
    raise NotImplementedError
