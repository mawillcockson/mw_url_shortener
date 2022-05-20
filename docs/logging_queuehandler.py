"""
demonstrates logging.QueueHandler
"""
import asyncio
import logging
import logging.config
from logging import StreamHandler
from logging.handlers import QueueHandler, QueueListener


def configure_logging() -> None:
    "configures logging for this demo"
    queue = asyncio.Queue()

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "formatter": {},
            },
            "filters": {
                "filter": {},
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "formatter",
                    "filters": ["filter"],
                    "stream": "ext://sys.stdout",
                },
                "queue_handler": {
                    "class": "logging.handlers.QueueHandler",
                    "level": "DEBUG",
                    "queue": queue,
                },
                "queue_listener": {
                    "class": "logging.handlers.QueueListener",
                    "queue": queue,
                    "respect_handler_level": False,
                    "handlers": ["cfg://handlers.stdout"],
                },
            },
            "loggers": {},
            "root": {
                "level": "DEBUG",
                "propagate": False,
                "filters": [],
                "handlers": ["queue_handler"],
            },
            "incremental": False,
        }
    )


async def main() -> None:
    "start functions that send log messages"

    logger = logging.getLogger(__name__)

    async def log(message: str) -> None:
        "logs a message"
        logger.info(message)

    await asyncio.gather(
        log("1"),
        log("2"),
        log("3"),
    )


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
