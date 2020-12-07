print(f"imported mw_url_shortener.console as {__name__}")
"""
The main cli frontend for the program

Primarily uses: https://github.com/Woile/decli
"""
from decli import cli
from . import config, version
from typing import Callable
import sys

def raise_not_implemented_gen(message: str) -> Callable[[], None]:
    """
    Make a function that will raise a NotImplemented error with a custom
    message
    """
    def not_implemented() -> None:
        raise NotImplementedError(message)

    return not_implemented

interface_spec = {
    "description": "Runs, creates, and interacts with a URL shortener",
    "add_help": True,
    "allow_abbrev": True,
    "subcommands": {
        "title": "subcommands title",
        "description": "subcommands description",
        "commands": [
            {
                "name": "server",
                "func": server.run,
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
            {
                "name": "version",
                "func": version.print_version,
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
    args_dict = args.__dict__

    if "func" not in args_dict:
        # No subcommand was specified:
        # $ mw_url_shortener
        parser.print_usage()
        sys.exit("Hint: try the 'config' sub-command")

    func = args_dict.pop("func")
    func(**args_dict)


if __name__ == "__main__":
    main()
