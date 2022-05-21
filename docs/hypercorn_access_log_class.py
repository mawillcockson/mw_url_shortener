"""
Either this file can create an hypercorn.logging.AccessLogger subclass that outputs JSON logs, following this line of advice:
https://pgjones.gitlab.io/hypercorn/how_to_guides/logging.html#customising-the-access-logger

Or the "hypercorn.error" logger configuration may be able to be overridden when the app is loaded by hypercorn.
"""
from hypercorn.logging import Logger

if False:

    class Logger:
        def __init__(self, config: "Config") -> None:
            self.access_log_format = config.access_log_format

            self.access_logger = _create_logger(
                "hypercorn.access",
                config.accesslog,
                config.loglevel,
                sys.stdout,
                propagate=False,
            )
            self.error_logger = _create_logger(
                "hypercorn.error", config.errorlog, config.loglevel, sys.stderr
            )

            if config.logconfig is not None:
                log_config = {
                    "__file__": config.logconfig,
                    "here": os.path.dirname(config.logconfig),
                }
                fileConfig(
                    config.logconfig,
                    defaults=log_config,
                    disable_existing_loggers=False,
                )
            else:
                if config.logconfig_dict is not None:
                    dictConfig(config.logconfig_dict)

        async def access(
            self, request: "WWWScope", response: "ResponseSummary", request_time: float
        ) -> None:
            if self.access_logger is not None:
                self.access_logger.info(
                    self.access_log_format, self.atoms(request, response, request_time)
                )

        async def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
            if self.error_logger is not None:
                self.error_logger.critical(message, *args, **kwargs)

        async def error(self, message: str, *args: Any, **kwargs: Any) -> None:
            if self.error_logger is not None:
                self.error_logger.error(message, *args, **kwargs)

        async def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
            if self.error_logger is not None:
                self.error_logger.warning(message, *args, **kwargs)

        async def info(self, message: str, *args: Any, **kwargs: Any) -> None:
            if self.error_logger is not None:
                self.error_logger.info(message, *args, **kwargs)

        async def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
            if self.error_logger is not None:
                self.error_logger.debug(message, *args, **kwargs)

        async def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
            if self.error_logger is not None:
                self.error_logger.exception(message, *args, **kwargs)

        async def log(
            self, level: int, message: str, *args: Any, **kwargs: Any
        ) -> None:
            if self.error_logger is not None:
                self.error_logger.log(level, message, *args, **kwargs)

        def atoms(
            self, request: "WWWScope", response: "ResponseSummary", request_time: float
        ) -> Mapping[str, str]:
            """Create and return an access log atoms dictionary.

            This can be overidden and customised if desired. It should
            return a mapping between an access log format key and a value.
            """
            return AccessLogAtoms(request, response, request_time)

        def __getattr__(self, name: str) -> Any:
            return getattr(self.error_logger, name)


class JSONLogger(Logger):
    def __init__(self, config: "Config") -> None:
        self.access_log_format = config.access_log_format

        self.access_logger = _create_logger(
            "hypercorn.access",
            config.accesslog,
            config.loglevel,
            sys.stdout,
            propagate=False,
        )
        self.error_logger = _create_logger(
            "hypercorn.error", config.errorlog, config.loglevel, sys.stderr
        )

        if config.logconfig is not None:
            log_config = {
                "__file__": config.logconfig,
                "here": os.path.dirname(config.logconfig),
            }
            fileConfig(
                config.logconfig,
                defaults=log_config,
                disable_existing_loggers=False,
            )
        else:
            if config.logconfig_dict is not None:
                dictConfig(config.logconfig_dict)

    async def access(
        self, request: "WWWScope", response: "ResponseSummary", request_time: float
    ) -> None:
        print(
            f"request:\n{request}\n\n"
            f"response:\n{response}\n\n"
            f"request_time: {request_time}",
            flush=True,
        )
        return await super().access(
            request=request, response=response, request_time=request_time
        )
