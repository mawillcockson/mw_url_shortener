"""
the common options and initialization for actions with a remote api
"""
import asyncio
import sys
from functools import partial
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, Container

import typer
from httpx import AsyncClient, HTTPStatusError, Response

from mw_url_shortener.dependency_injection import (
    get_async_loop,
    get_settings,
    inject_interface,
    inject_resource,
    reconfigure_dependency_injection,
)
from mw_url_shortener.interfaces import RedirectInterface, UserInterface
from mw_url_shortener.interfaces import remote as remote_interface
from mw_url_shortener.remote.start import make_async_client
from mw_url_shortener.schemas.user import Password, UserCreate, Username
from mw_url_shortener.settings import CliMode, Settings, defaults

from .common_subcommands import SHOW_CONFIGURATION_COMMAND_NAME, show_configuration
from .redirect import app as redirect_app
from .user import app as user_app

if TYPE_CHECKING:
    from typing import (
        Awaitable,
        Callable,
        Dict,
        List,
        Literal,
        Mapping,
        Optional,
        Tuple,
    )

    StatusMap = Mapping[Tuple[str, str], Container[int]]
    EventHook = Callable[[Response], Awaitable[None]]


class AnyStatusCode(Container[int]):
    def __contains__(self, value: object) -> "Literal[True]":
        if not isinstance(value, int):
            raise NotImplementedError(f"can only compare ints")
        return True


class OkStatus:
    standard_acceptable = [200, 401]
    acceptable_status_codes: "StatusMap" = {
        ("GET", "/v0/user/me"): standard_acceptable,
        ("GET", "/v0/user/"): standard_acceptable,
        ("POST", "/v0/user/"): standard_acceptable,
        ("PUT", "/v0/user/"): standard_acceptable,
        ("DELETE", "/v0/user/"): standard_acceptable,
        ("GET", "/v0/redirect/match/"): AnyStatusCode(),
        ("GET", "/v0/redirect/"): standard_acceptable,
        ("POST", "/v0/redirect/"): standard_acceptable,
        ("PUT", "/v0/redirect/"): standard_acceptable,
        ("DELETE", "/v0/redirect/"): standard_acceptable,
        ("POST", "/v0/security/token"): [200],
    }

    def __init__(self, settings: "Optional[Settings]" = None):
        if settings is None:
            settings = get_settings()
        self.settings = settings

        new_acceptable_status_codes: "Dict[Tuple[str, str], Container[int]]" = {}
        for method, endpoint in self.acceptable_status_codes:
            url = f"{settings.api_base_url}{endpoint}"
            new_acceptable_status_codes[(method, url)] = self.acceptable_status_codes[
                (method, endpoint)
            ]

        self.acceptable_status_codes = new_acceptable_status_codes

    def __call__(self, response: "Response") -> bool:
        return response.status_code in self[response]

    def __getitem__(self, response: "Response") -> "Container[int]":
        method = response.request.method.upper()
        url = str(response.request.url)
        for method, url_or_endpoint in self.acceptable_status_codes:
            if method == method and url.startswith(url_or_endpoint):
                return self.acceptable_status_codes[(method, url_or_endpoint)]
        return ()


def raise_for_non_200_or_401(
    settings: "Optional[Settings]" = None,
) -> "EventHook":
    """
    for most of the endpoints, the api will only respond with a 200 if
    everything went okay, and 401 if authentication is needed, which will be
    handled by the auth flow handler

    any other HTTP response status code is an error
    """
    ok_status = OkStatus(settings)

    async def raiser(response: Response) -> None:
        if not ok_status(response):
            method = response.request.method.upper()
            url = response.request.url
            expected_status_codes = ok_status[response]
            status_code = response.status_code
            phrase = HTTPStatus(status_code).phrase
            message = (
                f"for a {method} on url '{url}', "
                f"expected a status code of '{expected_status_codes}', "
                f"but got '{status_code} {phrase}'"
            )
            raise HTTPStatusError(
                message=message,
                request=response.request,
                response=response,
            )

    return raiser


def callback(
    ctx: typer.Context,
    base_url: str = typer.Option(
        ...,
        help="the first part of the URL of the API, "
        "or everything before the /openapi.json part "
        "(https://example.org/all/part/of/base/url/openapi.json)",
    ),
    # NOTE:FEAT it would be nice not to have to enter this if just using --help or --show-completion
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
) -> None:
    if (
        ctx.resilient_parsing
        or ctx.invoked_subcommand is None
        or "--help" in sys.argv
        or "--show-completion" in sys.argv
    ):
        return

    assert UserCreate(
        username=username, password=password
    ), "username and password must be valid"

    settings = get_settings()
    settings.cli_mode = CliMode.remote_api
    settings.base_url = base_url

    if ctx.invoked_subcommand == SHOW_CONFIGURATION_COMMAND_NAME:
        return

    raiser = raise_for_non_200_or_401(settings)
    event_hooks: "Dict[str, List[EventHook]]" = {"response": [raiser]}
    headers = {"User-Agent": settings.user_agent_string}
    async_client = AsyncClient(
        auth=remote_interface.OAuth2PasswordBearerHandler(
            settings=settings,
            username=Username(username),
            password=Password(password),
        ),
        event_hooks=event_hooks,
        max_redirects=3,
        base_url=settings.api_base_url,
        headers=headers,
    )
    loop = get_async_loop()
    resource_injector = partial(inject_resource, resource=async_client)

    user_interface_injector = partial(
        inject_interface,
        interface_type=UserInterface,
        interface=remote_interface.user,
    )

    redirect_interface_injector = partial(
        inject_interface,
        interface_type=RedirectInterface,
        interface=remote_interface.redirect,
    )

    reconfigure_dependency_injection(
        [resource_injector, user_interface_injector, redirect_interface_injector]
    )


app = typer.Typer(callback=callback)
app.command(name=SHOW_CONFIGURATION_COMMAND_NAME)(show_configuration)

app.add_typer(user_app, name="user")
app.add_typer(redirect_app, name="redirect")
