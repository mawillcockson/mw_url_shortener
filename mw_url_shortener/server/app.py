"""
this module is meant to be imported by hypercorn, after having configuration set by environment
variables

in testing, the mw-redir-server --help shows how to run the server

the code in mw_url_shortener.server.cli shows how to run the server in production

briefly, in a systemd service file:

[Service]
Environment=MAKE_APP=true
Environment=MW_URL_SHORTENER__DATABASE_PATH="/path/to/database file"
Environment=MW_URL_SHORTENER__JWT_SECRET_KEY="super secret key"
Type=forking
GuessMainPID=no
PIDFIle=/path/to/pid/file
# just a bit longer than --graceful-timeout below
TimeoutStopSec=12
ExecStart=/path/to/virtualenv/python -m hypercorn \\
        --worker-class uvloop \\
        --workers 4 \\
        --access-logfile - \\
        --error-logfile - \\
        --log-level INFO \\
        --insecure-bind 0.0.0.0:8000 \\
        --insecure-bind [::]:8000 \\
        --server-name url-shortener.example.com
        --graceful-timeout 10 \\
        --pid /path/to/pid/file
        mw_url_shortener.server.app:app

these docs links describe the syntax:

https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Environment
https://www.freedesktop.org/software/systemd/man/systemd.service.html#Options
"""
from os import environ
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from fastapi import FastAPI

    from mw_url_shortener.server.settings import ServerSettings


def make_fastapi_app(server_settings: "ServerSettings") -> "FastAPI":
    from functools import partial

    import inject

    from mw_url_shortener.dependency_injection import install_configurators
    from mw_url_shortener.server.settings import inject_server_settings

    server_settings_injector = partial(
        inject_server_settings, server_settings=server_settings
    )

    configurators = [
        server_settings_injector,
    ]

    injector = partial(install_configurators, configurators=configurators)

    inject.configure(injector)

    from fastapi import FastAPI

    from .routes.dependencies.security import oauth2_scheme
    from .routes.v0 import api_router as api_router_v0
    from .routes.v0.redirect import match
    from .routes.v0.security import login_for_access_token
    from .routes.v0.security import router as api_router_v0_security

    oauth2_scheme.model.flows.password.tokenUrl = str(server_settings.oauth2_endpoint)  # type: ignore

    api_router_v0_security.post(f"/{server_settings.oauth2_endpoint}")(
        login_for_access_token
    )

    if server_settings.api_prefix and not server_settings.api_prefix.endswith("/"):
        server_settings.api_prefix = server_settings.api_prefix + "/"
    if server_settings.root_path:
        if not server_settings.root_path.startswith("/"):
            server_settings.root_path = "/" + server_settings.root_path
        if not server_settings.root_path.endswith("/"):
            server_settings.root_path = server_settings.root_path + "/"

    if not server_settings.show_docs:
        openapi_url: "Optional[str]" = None
        docs_url: "Optional[str]" = None
        redoc_url: "Optional[str]" = None
    else:
        openapi_url = f"/{server_settings.api_prefix}openapi.json"
        docs_url = f"/{server_settings.api_prefix}docs"
        redoc_url = f"/{server_settings.api_prefix}redoc"

    app = FastAPI(
        title=server_settings.fast_api_title,
        description=server_settings.fast_api_description,
        version=server_settings.version,
        terms_of_service=server_settings.fast_api_terms_of_service,
        license_info=server_settings.fast_api_license_info.dict(),
        openapi_url=openapi_url,
        docs_url=docs_url,
        redoc_url=redoc_url,
        root_path=server_settings.root_path,
    )

    from .logging import (
        HTTPException,
        LoggingAPIRoute,
        RequestValidationError,
        custom_request_validation_exception_handler,
        logging_http_exception_handler,
    )

    app.router.route_class = LoggingAPIRoute
    app.exception_handler(HTTPException)(logging_http_exception_handler)
    app.exception_handler(RequestValidationError)(
        custom_request_validation_exception_handler
    )

    app.include_router(api_router_v0, prefix=f"/{server_settings.api_prefix}v0")
    app.post(f"/{server_settings.api_prefix}{server_settings.oauth2_endpoint}")(
        login_for_access_token
    )
    # since this matches almost every GET request, it should come last so that
    # other, more specific endpoints are matched first
    app.get("/{short_link:path}")(match)

    from asgi_correlation_id import CorrelationIdMiddleware

    from mw_url_shortener.schemas.log import CORRELATION_ID_HEADER_NAME

    # NOTE:BUG if multiple requests have a header named
    # CORRELATION_ID_HEADER_NAME with the same value, there could be some
    # confusion in the logs as to which log entries correspond to which request
    # Ideally, a new middleware would be created that doesn't read any headers,
    # and always creates a new correlation id for each incoming request.
    app.add_middleware(
        CorrelationIdMiddleware,
        header_name=CORRELATION_ID_HEADER_NAME,
        validate_header_as_uuid=False,
    )

    return app


if "MAKE_APP" in environ:
    from mw_url_shortener.server.settings import ServerSettings

    server_settings = ServerSettings()
    app = make_fastapi_app(server_settings)
