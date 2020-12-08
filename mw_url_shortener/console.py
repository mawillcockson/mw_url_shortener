print(f"imported mw_url_shortener.console as {__name__}")
"""
The main cli frontend for the program

Primarily uses: https://github.com/Woile/decli
"""
from decli import cli
from . import config, __version__
from .config import CommonSettings
from typing import Callable, Union, Optional
from pydantic import BaseSettings
import sys
from argparse import ArgumentTypeError, Namespace
from pathlib import Path


class ArgumentValidationError(ArgumentTypeError, TypeError):
    "subclasses both argparse.ArgumentTypeError and TypeError"
    pass


class OpenableFileMeta(type):
    "Only here to make OpenableFile a callable class"
    def __call__(self, filename: Union[Path, str, type(None)]) -> Path:
        "checks that the filename is a valid path, and returns it"
        path = Path(filename).resolve()
        if not path.is_file():
            raise ArgumentValidationError(f"'{path}' is not a file")

        try:
            file = path.open(mode="rb")
        except OSError as err:
            raise ArgumentValidationError(f"cannot open '{path}'")
        finally:
            file.close()

        return path


class OpenableFile(metaclass=OpenableFileMeta):
    "Will only take a file that's able to be read"
    pass


def raise_not_implemented_gen(message: str) -> Callable[[], None]:
    """
    Make a function that will raise a NotImplemented error with a custom
    message
    """
    def not_implemented() -> None:
        raise NotImplementedError(message)

    return not_implemented


def server_run(args: Namespace) -> None:
    """
    Obtains all configuration information for the server, then runs the server
    """
    # NOTE: import here so that it's not imported when console is imported and
    # run, to keep load times down
    from . import server
    common_keys = list(CommonSettings.__fields__)
    non_common_settings = {k:v for k,v in server.Settings.from_orm(args).dict().items() if k not in common_keys}
    server.run(**non_common_settings)

interface_spec = {
    "description": "Runs, creates, and interacts with a URL shortener",
    "add_help": True,
    "allow_abbrev": True,
    "arguments": [
        {
            "name": "--version",
            "action": "version",
            "version": f"%(prog)s {__version__}",
            "help": "prints the version",
        },
        {
            "name": ["-c", "--env-file"],
            "type": OpenableFile,
            "default": None,
            "help": "config file in python-dotenv format",
        },
    ],
    "subcommands": {
        "title": "subcommands title",
        "description": "subcommands description",
        "commands": [
            {
                "name": "server",
                "func": server_run,
                "arguments": [
                    {
                        "name": ["--reload"],
                        "action": "store_true",
                        "help": "Watch the server files and reload the server when those files change (used in development)",
                        "group": "dev",
                    },
                ],
            },
            {
                "name": "client",
                "func": raise_not_implemented_gen("No client command")
            },
            {
                "name": "config",
                "func": raise_not_implemented_gen("No config command")
            },
        ],
    },
}

def main() -> None:
    """
    Parses the cli arguments and runs the appropriate commands
    """
    parser = cli(interface_spec)
    args = parser.parse_args()

    if "func" not in args:
        # No subcommand was specified:
        # $ mw_url_shortener
        parser.print_usage()
        sys.exit("Hint: try the 'config' sub-command")

    args.func(args=args)


if __name__ == "__main__":
    main()
