print(f"imported mw_url_shortener.config as {__name__}")
"""
where the global application configuration is retrieved and modified
"""
import os
from argparse import Namespace
from collections.abc import Mapping
from pathlib import Path
from typing import Dict, NamedTuple, Optional

import pydantic
from pydantic import BaseModel, Field, ValidationError, constr, root_validator

from . import settings
from .database.config import get_config as get_from_db
from .database.config import save_config as save_to_db
from .database.errors import BadConfigInDBError
from .settings import CommonSettings, SettingsClassName

# From:
# https://stackoverflow.com/a/2821183
# https://stackoverflow.com/questions/2821043/allowed-characters-in-linux-environment-variable-names/2821183#2821183
EnvVarName = constr(min_length=1, regex=r"^[A-Z]([A-Z0-9_]+)?$")


class SettingsEnvNames(BaseModel):
    "names of the environment variables for the settings class and values"
    class_name: EnvVarName
    value_name: EnvVarName

    # Don't run this validator when the type validation fails
    @root_validator(skip_on_failure=True)
    def different_values(cls, values: Dict[str, EnvVarName]) -> Dict[str, EnvVarName]:
        "are the class name and value name different"
        print(values)
        assert values.get("class_name", False), "class_name must not be empty"
        assert values.get("value_name", False), "value_name must not be empty"
        assert (
            values["class_name"] != values["value_name"]
        ), "variable names must be different"
        return values


class BadConfigError(Exception):
    "the configuration data did not conform to the settings model"
    pass


class BadEnvConfigError(BadConfigError):
    "the config found in the environment was not correct"
    pass


def update_module_cache(new_settings: CommonSettings) -> CommonSettings:
    "updates the internally cached settings"
    if settings._settings is None:
        raise TypeError(
            "cannot update settings since settings have not been set; call set()"
        )

    if not isinstance(new_settings, CommonSettings):
        raise TypeError(
            f"new_settings must be a {CommonSettings.__name__} subclass; got '{new_settings.__qualname__}'"
        )

    settings._settings = new_settings(**new_settings.dict())
    return settings._settings


def settings_env_names(
    settings_class: CommonSettings = CommonSettings,
) -> NamedTuple:
    """
    returns the current environment variable names for the settings class and
    value
    """
    try:
        _ = SettingsClassName.validate(settings_class)
    except (ValidationError, ValueError) as err:
        raise ValueError(
            f"settings_class must be one of ({', '.join(SettingsClassName._class_names)})"
        ) from err

    env_config = settings_class.Config()
    try:
        env_prefix = EnvVarName.validate(env_config.env_prefix)
    except (AttributeError, TypeError, pydantic.errors.StrRegexError) as err:
        raise ValueError(
            "settings_class must have a valid env_prefix configured"
        ) from err
    value_name = f"{env_prefix}_settings".upper()
    class_name = f"{value_name}_class".upper()

    return SettingsEnvNames(class_name=class_name, value_name=value_name)


def set_env(
    new_settings: CommonSettings, env_names_or_none: Optional[SettingsEnvNames] = None
) -> None:
    """
    sets the environment variables associated with the class of the settings
    object to their value in the settings object
    """
    if env_names_or_none is not None and not isinstance(
        env_names_or_none, SettingsEnvNames
    ):
        raise TypeError("env_names must be a SettingsEnvNames or None")

    if not isinstance(new_settings, CommonSettings):
        raise TypeError(
            "new_settings must be instantiated from "
            f"{CommonSettings.__name__} or a subclass"
        )

    settings_class = type(new_settings)
    settings_class_name = settings_class.__name__

    try:
        SettingsClassName.validate(settings_class)
    except (ValidationError, ValueError) as err:
        raise ValueError(
            f"new_settings must be one of ({', '.join(SettingsClassName._class_names)})"
        ) from err

    if env_names_or_none is None:
        env_names = settings_env_names()
    else:
        env_name = env_names_or_none

    settings_json = new_settings.json()
    assert new_settings == settings_class.parse_raw(
        settings_json
    ), "settings must be able to be serialized and deserialized"

    os.environ[env_names.class_name] = settings_class_name
    os.environ[env_names.value_name] = settings_json


def get_env(env_names_or_none: SettingsEnvNames = None) -> CommonSettings:
    "gets the current settings from the environment"
    if env_names_or_none is not None and not isinstance(
        env_names_or_none, SettingsEnvNames
    ):
        raise TypeError("env_names must be a SettingsEnvNames or None")

    if env_names_or_none is None:
        env_names = settings_env_names()
    else:
        env_name = env_names_or_none

    settings_class_name = os.getenv(env_names.class_name, None)
    settings_value = os.getenv(env_names.value_name, None)
    if settings_class_name is None or settings_value is None:
        raise ValueError("environment not set")

    settings_class = getattr(settings, settings_class_name, None)
    if settings_class is None or not issubclass(settings_class, CommonSettings):
        raise ValueError(f"cannot find class '{settings_class_name}'")

    return settings_class.parse_raw(settings_value)


def set(
    args: Optional[Namespace] = None, settings_class: CommonSettings = CommonSettings
) -> CommonSettings:
    if not isinstance(args, (Namespace, type(None))):
        raise TypeError("args must be an argparse.Namespace or None")
    if not issubclass(settings_class, CommonSettings):
        raise TypeError("settings_class must be a subclass of settings.CommonSettings")

    # The ordering is important, as the later ones override the earlier ones if
    # they both have the same key
    # >>> a = {"z": 0}
    # >>> b = {"z": 1}
    # >>> {**a, **b}
    # {'z': 1}
    extra_settings = dict()
    if isinstance(settings._settings, Mapping):
        extra_settings.update(settings._settings)
    if isinstance(args, Namespace):
        extra_settings.update(vars(args))

    preliminary_settings = CommonSettings(env_file=extra_settings.get("env_file", None))

    pre_and_extra_settings = preliminary_settings.dict()
    pre_and_extra_settings.update(extra_settings)

    if not isinstance(preliminary_settings.env_file, (Path, str)):
        full_settings = settings_class(**pre_and_extra_settings)
    else:
        env_file = Path(preliminary_settings.env_file).resolve()
        try:
            env_file.read_text()
        except OSError as err:
            raise ValueError(f"cannot open .env file at '{env_file}'") from err

        full_settings = settings_class(_env_file=env_file, **preliminary_settings)

    settings._settings = full_settings
    return full_settings


def get() -> CommonSettings:
    """
    obtains configuration information

    the order of precedence from lowest priority to highest is:
    - defaults on the class
    - .env file
    - environment
    - previously set settings
    - args
    """
    if isinstance(settings._settings, Mapping):
        return settings._settings

    env_prefix: str = CommonSettings.Config().env_prefix
    env_name = f"{env_prefix}__settings_class_name"
    settings_class_name: Optional[str] = os.getenv(env_name, default=None)
    if settings_class_name is None or not hasattr(settings, settings_class_name):
        raise ValueError(
            f"expected environment variable '{env_name.upper()}' "
            "to be set with the name of the settings class"
        )

    settings_class = getattr(settings, settings_class_name)
    settings._settings = settings_class()
    return setting._settings
