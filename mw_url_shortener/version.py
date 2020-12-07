print(f"imported mw_url_shortener.version as {__name__}")
from . import __version__


def print_version() -> str:
    "prints and returns the current version"
    print(__version__)
    return __version__
