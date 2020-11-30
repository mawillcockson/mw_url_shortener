from . import __version__


def print_version() -> str:
    "prints and returns the current version"
    print(__version__)
    return __version__
