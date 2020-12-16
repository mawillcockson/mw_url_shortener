print(f"imported mw_url_shortener.config as {__name__}")
"""
where the global application configuration is retrieved and modified
"""
import os
from argparse import Namespace
from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple, Optional

from . import settings
from .settings import CommonSettings


class SettingsEnvNames(NamedTuple):
    "names of the environment variables for the settings class and values"
    class_name: str
    value_name: str


class BadEnvConfigError(Exception):
    "the config found in the environment was not correct"
    pass


def update_cache(new_settings: CommonSettings) -> CommonSettings:
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
    base_settings_class: CommonSettings = CommonSettings,
) -> NamedTuple:
    """
    returns the current environment variable names for the settings class and
    value
    """
    env_prefix = base_settings_class.Config().env_prefix
    value_name = f"{env_prefix}__settings".upper()
    class_name = f"{value_name}_class".upper()

    return SettingsEnvNames(class_name=class_name, value_name=value_name)


def set_env(new_settings: CommonSettings, env_names: SettingsEnvNames) -> None:
    """
    sets the environment variables associated with the class of the settings
    object to their value in the settings object
    """
    if not isinstance(new_settings, CommonSettings):
        raise TypeError(
            "new_settings must be instantiated from "
            f"{CommonSettings.__name__} or a subclass"
        )

    settings_class_name = new_settings.__class__.__name__

    class_err_msg = (
        f"don't know where to find '{settings_class_name}'; " "not in .settings module"
    )

    if not hasattr(settings, settings_class_name):
        raise ValueError(class_err_msg)

    new_settings_class = getattr(settings, settings_class_name)

    if new_settings_class != type(new_settings):
        raise ValueError(class_err_msg)

    settings_json = new_settings.json()
    assert new_settings == new_settings_class.parse_raw(
        settings_json
    ), "settings must be able to be serialized and deserialized"

    os.environ[env_names.class_name] = settings_class_name
    os.environ[env_names.value_name] = settings_json


def get_env(env_names: SettingsEnvNames) -> CommonSettings:
    "gets the current settings from the environment"
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
