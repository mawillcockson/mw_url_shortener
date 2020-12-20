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


@pytest.mark.xfail
def test_settings_env_names_func_no_env_prefix() -> None:
    """
    is an error raised if the settings class does not define a valid
    env_prefix
    """
    raise NotImplementedError


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


@pytest.mark.xfail
def test_set_env_bad_types(monkeypatch: pytest.MonkeyPatch) -> None:
    "does set_env raise an error when the arguments are the wrong types"
    raise NotImplementedError


@pytest.mark.xfail
def test_set_env_non_serializable(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    does set_env throw an error when the settings can't be serialized into a
    string
    """
    raise NotImplementedError


@pytest.mark.xfail
def test_set_env_bad_env_names(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    does set_env raise an error when it's given bad environment variable names
    """
    raise NotImplementedError


@pytest.mark.xfail
def test_set_env_bad_settings_class(correct_settings: CommonSettings) -> None:
    """
    does set_env raise an error when the name of the settings class matches,
    but isn't one from the settings module
    """

    class DummySettings(CommonSettings):
        pass

    dummy = DummySettings(**correct_settings.dict())
    dummy.__class__.__name__ = CommonSettings.__name__
    assert type(dummy).__name__ == CommonSettings.__name__

    with pytest.raises(TypeError) as err:
        config.set_env(env_names=env_names, new_settings=dummy)
    assert (
        f"don't know where to find '{dummy.__class__.__name__}'; not in .settings module"
        in str(err.value)
    )


@pytest.mark.xfail
def test_set_env_same_env_names() -> None:
    """
    does set_env raise an error when the names specified for the environment
    variable are the same
    """
    raise NotImplementedError


@pytest.mark.xfail
def test_get_env_bad_types() -> None:
    "is an error raised when it's passed bad arguments"

    env_names = SettingsEnvNames()

    with pytest.raises(TypeError) as err:
        config.get_env(env_names=env_names)
    assert (
        "env_names bust be a SettingsEnvNames of strings naming the environment variables to look in"
        in str(err.value)
    )


@pytest.mark.xfail
def test_get_env_bad_class_name() -> None:
    "is an error raised when the environment variable has a bad class name"
    raise NotImplementedError


@pytest.mark.xfail
def test_get_env_vars_not_set() -> None:
    "is an error raised when the environmet variables aren't set"
    raise NotImplementedError


@pytest.mark.xfail
def test_get_env_vars_empty() -> None:
    "is an error raised when the environment variables are set to empty strings"
    raise NotImplementedError


@pytest.mark.xfail
def test_get_env_vars_non_deserializable() -> None:
    "will an error be raised if the environment variable has a string that can't be deseriealized"
    raise NotImplementedError


@pytest.mark.xfail
def test_get_env_extra_properties() -> None:
    "will extra properties not part of the settings class be allowed"
    raise NotImplementedError


@pytest.mark.xfail
def test_get_priorities() -> None:
    """
    is the priority of the sources for configuration information:
    defaults < dotenv < env vars < database < args
    """
    raise NotImplementedError


@pytest.mark.xfail
def test_get_updates_db() -> None:
    "is the cache in the database updated"
    raise NotImplementedError


@pytest.mark.xfail
def test_get_updates_env() -> None:
    "is the environment updated"


@pytest.mark.xfail
def test_get_updates_module_cache() -> None:
    "is the cache in the settings module updated"
    raise NotImplementedError


@pytest.mark.xfail
def test_get_updates_everwhere() -> None:
    "is the environment, database, and cache all updated to match"
    raise NotImplementedError


@pytest.mark.xfail
def test_save_updates_env() -> None:
    "is the environment updated"
    raise NotImplementedError


@pytest.mark.xfail
def test_save_updates_db() -> None:
    "is the database updated"
    raise NotImplementedError


@pytest.mark.xfail
def test_save_updates_module_cache() -> None:
    "is the cache in the settings module updated"
    raise NotImplementedError


@pytest.mark.xfail
def test_save_updates_everywhere() -> None:
    "is the environment, database, and cache all updated to match"
    raise NotImplementedError


@pytest.mark.xfail
def test_save_allow_bad_db() -> None:
    """
    will updating the database be skipped if the database file points to a bad
    database
    """
    raise NotImplementedError


@pytest.mark.xfail
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


@pytest.mark.xfail
def test_export() -> None:
    "config.export()"
    raise NotImplementedError


@pytest.mark.xfail
def test_write_dotenv() -> None:
    "config.write_dotenv()"
    raise NotImplementedError
