"""
ensures mw_url_shortener.config behaves correctly
"""
import os
from pathlib import Path
from typing import Dict, NamedTuple, Tuple, Union

import pytest
from pydantic import ValidationError

from mw_url_shortener import config
from mw_url_shortener.config import Namespace
from mw_url_shortener.settings import (
    CommonSettings,
    DatabaseSettings,
    SettingsClassName,
)

def test_environment_isolation_set(random_env_var_names: Tuple[str, str]) -> None:
    "set environment variables that _check will look for"
    assert os.getenv(random_env_var_names[0], None) is None
    assert os.getenv(random_env_var_names[1], None) is None
    os.environ[random_env_var_names[0]] = "example"
    os.putenv(random_env_var_names[1], "demo")
    assert os.getenv(random_env_var_names[0], None) == "example"
    # NOTE:BUG why is the below statement true?????
    assert os.getenv(random_env_var_names[1], None) is None


def test_environment_isolation_check(random_env_var_names: Tuple[str, str]) -> None:
    """
    checks to make sure the environment variables set in one test don't show up
    in another test
    """
    assert os.getenv(random_env_var_names[0], None) is None
    assert os.getenv(random_env_var_names[1], None) is None
    with pytest.raises(KeyError):
        os.environ[random_env_var_names[0]]
    with pytest.raises(KeyError):
        os.environ[random_env_var_names[1]]


# NOTE:TESTS::RANDOMIZATION
@pytest.mark.parametrize(
    "class_name,value_name",
    [
        (object(), int(1)),
        (int(1), object()),
        ("9", "VALID_INPUT"),
        ("", "VALID_INPUT"),
        ("VALID_INPUT", "9"),
        ("VAlID_INPUT", ""),
        ("", ""),
        ("not valid", "NOT-VALID"),
    ],
)
def test_settings_env_names_class_bad_input(
    class_name: Union[object, int, str], value_name: Union[object, int, str]
) -> None:
    "is an error raised on bad values and types"
    with pytest.raises(ValidationError) as err:
        config.SettingsEnvNames(class_name=class_name, value_name=value_name)


@pytest.mark.parametrize(
    "class_name,value_name",
    [
        ("VALID_INPUT", "GOOD_EXAMPLE"),
        ("PREFIX__SETTINGS_CLASS", "PREFIX__SETTINGS"),
        ("URL_SHORTENER__SETTINGS_CLASS", "URL_SHORTENER__SETTINGS"),
    ],
)
def test_settings_env_names_class(class_name: str, value_name: str) -> None:
    "are all of these valid environment variable names"
    config.SettingsEnvNames(class_name=class_name, value_name=value_name)


@pytest.mark.parametrize("settings_class", [object(), int(1), type])
def test_settings_env_names_func_bad_inputs(
    settings_class: Union[object, int, type]
) -> None:
    "is an error raised if bad inputs are given"
    with pytest.raises(ValueError) as err:
        config.settings_env_names(settings_class=settings_class)
    assert (
        f"settings_class must be one of ({', '.join(SettingsClassName._class_names)})"
        in str(err.value)
    )


def test_settings_env_names_func_bad_input(correct_settings: CommonSettings) -> None:
    "is a class with a proper name rejected with an error"

    class DummyClass(CommonSettings):
        f"a dummy class meant to mimic {CommonSettings.__name__}"
        pass

    DummyClass.__name__ = CommonSettings.__name__

    with pytest.raises(ValueError) as err:
        config.settings_env_names(settings_class=DummyClass)
    assert (
        f"settings_class must be one of ({', '.join(SettingsClassName._class_names)})"
        in str(err.value)
    )


def test_settings_env_names_func() -> None:
    f"is {CommonSettings.__name__} used by default"
    env_names_default = config.settings_env_names()
    env_names_commonsettings = config.settings_env_names(settings_class=CommonSettings)
    assert env_names_default == env_names_commonsettings
    assert isinstance(env_names_default.class_name, str)
    assert isinstance(env_names_default.value_name, str)


def test_set_and_get_env(
    correct_settings: CommonSettings, monkeypatch: pytest.MonkeyPatch
) -> None:
    "can settings make the round trip"
    config.set_env(correct_settings)
    returned_settings = config.get_env()
    assert returned_settings == correct_settings


def test_get_no_args_error() -> None:
    "does get() throw an error if no database file is given"
    with pytest.raises(ValidationError) as err:
        config.get(settings_class=DatabaseSettings)
    assert "database_file" in str(err.value)


@pytest.mark.xfail
@pytest.mark.parametrize("args", [object(), type, {"a": 1}])
def test_get_bad_type(args: Union[object, type, Dict[str, int]]) -> None:
    "does get raise a TypeError if args isn't a Namespace"
    with pytest.raises(TypeError) as err:
        config.get(args=args)
    assert "args must be an argparse.Namespace or None" in str(err.value)


@pytest.mark.xfail
def test_get_database_in_args(tmp_path: Path) -> None:
    "if the database_file is indicated in the args, is it then set in the environment"
    database_file = tmp_path / "temp.sqlitedb"
    resolved_database_file = database_file.resolve()
    resolved_database_file.touch()
    args = Namespace(database_file=database_file)
    settings = config.get(args=args, settings_class=DatabaseSettings)
    assert isinstance(settings, CommonSettings)
    assert settings.database_file == resolved_database_file
    assert os.getenv("URL_SHORTENER_DATABASE_FILE") == str(resolved_database_file)


@pytest.mark.xfail()
def test_from_db() -> None:
    "config.from_db()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_to_db() -> None:
    "config.to_db()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_save() -> None:
    "config.save()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_export() -> None:
    "config.export()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_write_dotenv() -> None:
    "config.write_dotenv()"
    raise NotImplementedError
