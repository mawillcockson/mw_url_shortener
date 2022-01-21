from http import HTTPStatus
from typing import TYPE_CHECKING, Container

from httpx import AsyncClient, HTTPStatusError, Response
from multipart.multipart import parse_options_header

from mw_url_shortener.dependency_injection import get_settings
from mw_url_shortener.interfaces import remote as remote_interface
from mw_url_shortener.interfaces.helpers import run_sync

from .authentication import OAuth2PasswordBearerHandler

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

    import inject

    StatusMap = Mapping[Tuple[str, str], Container[int]]
    EventHook = Callable[[Response], Awaitable[None]]

    from mw_url_shortener.schemas.user import Password, Username
    from mw_url_shortener.settings import Settings


class AnyStatusCode(Container[int]):
    def __contains__(self, value: object) -> "Literal[True]":
        if not isinstance(value, int):
            raise NotImplementedError(f"can only handle int status codes")
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


async def utf8_for_json(response: Response) -> None:
    content_type_header = response.headers.get("Content-Type", None)
    if not content_type_header:
        return
    content_type_value, _ = parse_options_header(content_type_header)
    if content_type_value != b"application/json":
        return
    response.encoding = "utf-8"


def make_async_client(
    settings: "Settings", username: "Username", password: "Password"
) -> AsyncClient:
    raiser = raise_for_non_200_or_401(settings)
    event_hooks: "Dict[str, List[EventHook]]" = {"response": [raiser, utf8_for_json]}
    headers = {"User-Agent": settings.user_agent_string}
    return AsyncClient(
        auth=OAuth2PasswordBearerHandler(
            settings=settings,
            username=username,
            password=password,
        ),
        event_hooks=event_hooks,
        max_redirects=3,
        base_url=settings.api_base_url,
        headers=headers,
    )


def make_async_client_closer(async_client: "AsyncClient") -> "Callable[[], None]":
    """
    if AsyncClient is opened and used outside a `with` block, then it's
    .aclose() method must be await-ed to clean up open connections before the
    application ends

    this function returns a callable that will do that

    it's meant to be used by click.Context.call_on_close()
    """

    def closer() -> None:
        "closes the wrapped httpx.AsyncClient"
        run_sync(async_client.aclose())

    return closer


def inject_async_client(
    binder: "inject.Binder", *, async_client: "AsyncClient"
) -> None:
    binder.bind("AsyncClient", async_client)
