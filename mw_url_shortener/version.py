print(f"imported mw_url_shortener.version as {__name__}")
from typing import Optional

from pydantic import BaseSettings

from . import __version__


# NOTE:FUTURE::DOCS Update docstring is the parameter is used
def print_version(settings: Optional[BaseSettings] = None) -> str:
    """
    prints and returns the current version

    the parameter is not used
    """
    print(__version__)
    return __version__
