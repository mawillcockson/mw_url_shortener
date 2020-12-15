print(f"imported mw_url_shortener.config as {__name__}")
"""
where the global application configuration is retrieved and modified
"""
from argparse import Namespace
from .settings import CommonSettings
from typing import Optional
from . import settings
from collections.abc import Mapping
from pathlib import Path


def get(args: Optional[Namespace] = None, settings_class: CommonSettings = CommonSettings) -> CommonSettings:
    """
    obtains configuration information

    the order of precedence from lowest priority to highest is:
    - defaults on the class
    - .env file
    - environment
    - previously set settings
    - args
    """
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
