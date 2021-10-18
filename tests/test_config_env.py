"""
ensures the environment portion of mw_url_shortener.config behaves correctly
"""
import os
from pathlib import Path
from typing import Dict, NamedTuple, Tuple, Union
from unittest.mock import patch

import pytest
from pydantic import BaseSettings, ValidationError

from mw_url_shortener import config, settings
from mw_url_shortener.config import Namespace
from mw_url_shortener.settings import (
    CommonSettings,
    DatabaseSettings,
    SettingsClassName,
    SettingsTypeError,
)

from .conftest import BadSettings


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
    env_names = config.SettingsEnvNames(class_name=class_name, value_name=value_name)
    assert env_names.class_name == class_name
    assert env_names.value_name == value_name


def test_same_env_names() -> None:
    """
    is an error raised when the names specified for the environment variable
    are the same
    """
    with pytest.raises(ValidationError) as err:
        config.SettingsEnvNames(class_name="A", value_name="A")
    assert "variable names must be different" in str(err.value)


@pytest.mark.parametrize("settings_class", [object(), int(1), type])
def test_settings_env_names_func_bad_inputs(
    settings_class: Union[object, int, type]
) -> None:
    "is an error raised if bad inputs are given"
    with pytest.raises(SettingsTypeError) as err:
        config.settings_env_names(settings_class=settings_class)
    assert (
        f"settings_class must be one of ({', '.join(SettingsClassName._class_names)})"
        in str(err.value)
    )


def test_settings_env_names_func_bad_input(bad_settings: BadSettings) -> None:
    "is a class with a proper name rejected with an error"
    assert SettingsClassName.validate(type(bad_settings).__name__)

    with pytest.raises(SettingsTypeError) as err:
        config.settings_env_names(settings_class=type(bad_settings))
    assert (
        f"settings_class must be one of ({', '.join(SettingsClassName._class_names)})"
        in str(err.value)
    )


def test_settings_env_names_func_no_env_prefix() -> None:
    """
    is an error raised if the settings class does not define a valid
    env_prefix
    """

    # Create a dummy settings class
    class MissingEnvPrefix(BaseSettings):
        "a dummy class"

        class Config:
            pass

    fake_classes = SettingsClassName._classes.copy()
    fake_classes.append(MissingEnvPrefix)

    with patch.object(SettingsClassName, "_classes", fake_classes):
        with pytest.raises(ValueError) as err:
            config.settings_env_names(settings_class=MissingEnvPrefix)

    assert "settings_class must have a valid env_prefix configured" in str(err.value)


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
    assert os.getenv("URL_SHORTENER__SETTINGS", None) == correct_settings.json()
    returned_settings = config.get_env()
    assert returned_settings == correct_settings


@pytest.mark.parametrize("value", [object(), int(-3), type])
def test_set_env_bad_types(
    correct_settings: CommonSettings, value: Union[object, int, type]
) -> None:
    "does set_env raise an error when env_names is the wrong type"
    with pytest.raises(TypeError) as err:
        config.set_env(new_settings=correct_settings, env_names_or_none=value)
    assert f"env_names must be a {config.SettingsEnvNames.__name__} or None" in str(err.value)


def test_set_env_non_serializable(correct_database_settings: DatabaseSettings) -> None:
    """
    does set_env throw an error when the settings can't be serialized into a
    string
    """
    unserializable_settings = correct_database_settings.copy(update={"unserializable": object()})
    
    with pytest.raises(TypeError):
        unserializable_settings.json()

    with pytest.raises(config.ConfigError) as err:
        config.set_env(new_settings=unserializable_settings)
    assert "settings must be able to be serialized and deserialized" in str(err.value)


def test_set_env_bad_serialization(correct_database_settings: DatabaseSettings) -> None:
    """
    does set_env raise an error when the settings can't be reliably
    deserialized
    """
    unreliable_settings = correct_database_settings.copy(update={"unreliable": {1,2,3}})

    assert unreliable_settings.json()

    with pytest.raises(config.ConfigError) as err:
        config.set_env(new_settings=unreliable_settings)
    assert "settings must be able to be serialized and deserialized" in str(err.value)


def test_set_env_bad_env_names(correct_settings: CommonSettings) -> None:
    """
    does set_env raise an error when it's given bad environment variable names
    """
    env_names = config.settings_env_names()
    class SettingsEnvNames(NamedTuple):
        f"a bad class meant to mimic {config.SettingsEnvNames.__name__}"
        class_name: str = env_names.class_name
        value_name: str = env_names.value_name
    
    with pytest.raises(TypeError) as err:
        config.set_env(new_settings=correct_settings, env_names_or_none=SettingsEnvNames())
    assert f"env_names must be a {config.SettingsEnvNames.__name__} or None" in str(err.value)


def test_set_env_bad_settings_class(bad_settings: BadSettings) -> None:
    """
    does set_env raise an error when the name of the settings class matches,
    but isn't one from the settings module
    """
    with pytest.raises(SettingsTypeError) as err:
        config.set_env(new_settings=bad_settings)
    assert (
        f"new_settings must be one of ({', '.join(SettingsClassName._class_names)})"
        in str(err.value)
    )


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


def test_extra_properties(correct_database_settings: DatabaseSettings) -> None:
    "will extra properties not part of the settings class be allowed"
    extra_properties_settings = correct_database_settings.copy(update={"extra": "example"})

    config.set_env(new_settings=extra_properties_settings)
    returned_settings = config.get_env()
    assert returned_settings == extra_properties_settings


@pytest.mark.xfail  # NOTE:NEXT
def test_get_updates_from_env(correct_settings: CommonSettings) -> None:
    "is the cache in the settings module updated"
    assert settings._settings is None
    env_names = config.settings_env_names()
    class_name = env_names.class_name
    value_name = env_names.value_name
    os.environ[class_name] = type(correct_settings).__name__
    os.environ[value_name] = correct_settings.json()

    returned_settings = config.get()
    assert os.getenv(class_name, None) == type(correct_settings).__name__
    assert os.getenv(value_name, None) == correct_settings.json()
    assert returned_settings == correct_settings
    assert settings._settings == correct_settings
