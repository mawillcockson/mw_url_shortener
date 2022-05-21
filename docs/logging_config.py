"""
demonstrates a few of the options for how to configure logging
https://docs.python.org/3/howto/logging-cookbook.html#context-info
https://docs.python.org/3/library/logging.handlers.html#memoryhandler
https://docs.python.org/3/library/logging.handlers.html#queuehandler
https://docs.python.org/3/library/asyncio-dev.html#logging
https://github.com/snok/asgi-correlation-id/blob/791ea1c6e43a3e8ff1698ed22d0965a75b7b1041/README.md
"""
import logging
import logging.config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, List

    Closer = Callable[[], None]
    from mw_url_shortener.settings import Settings

# Since HTTP doesn't seem to support an empty header name, using an empty
# header name should prevent a client from being able to set a correlation id
# in its request
# https://stackoverflow.com/a/58056620
CORRELATION_ID_HEADER_NAME: str = ""

KIBIBYTE: int = 1024
MEBIBYTE: int = KIBIBYTE ** 2
APP_NAME: str = "mw_url_shortener"

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "message_only": {
            "format": "{message}",
            "datefmt": "",
            "style": "{",
            # "class": "",  # custom class
        },
        "full": {
            "format": "[{asctime} {level:} {log_name}] {message}",
            "datefmt": "",
            "style": "{",
        },
        "simple": {
            "format": "[{asctime} {level:}] {message}",
            "datefmt": "",
            "style": "{",
        },
    },
    "filters": {
        # the server module should define it's own logging config dictionary
        # that include the correlation id log filter, tied to the
        # "mw_url_shortener.server" logger
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            # "filters": [],
            # named parameters for logging.StreamHandler
            "stream": "ext://sys.stderr",
        },
        # probably only the server needs a file logger, whereas the CLI is fine
        # with just a console logger
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "full",
            "level": "DEBUG",
            # named parameters for logging.handlers.RotatingFileHandler
            "filename": "server.log",
            "maxBytes": 10 * MEBIBYTE,
            "backupCount": int("inf"),  # don't delete old log files
        },
    },
    "loggers": {
        APP_NAME: {
            "level": "DEBUG",
            "propagate": True,
            # "filters": [],
            "handlers": ["console", "file"],
        },
    },
    "root": {
        "level": "DEBUG",
        # "filters": [],
        "handlers": ["console", "file"],
    },
    "incremental": False,
    "disable_existing_loggers": True,
}


def configure_logging(settings: "Settings") -> "List[Closer]":
    logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
    return []
