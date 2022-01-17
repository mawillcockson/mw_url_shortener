import asyncio
from typing import (
    TYPE_CHECKING,
    AsyncGenerator,
    Awaitable,
    Dict,
    Generator,
    Literal,
    Optional,
    cast,
)

import inject
import pydantic
from httpx import Auth, HTTPStatusError, Request, Response

from mw_url_shortener.schemas.security import (
    AccessToken,
    AuthorizationHeaders,
    OAuth2PasswordRequestFormData,
    make_authorization_headers,
)
from mw_url_shortener.schemas.user import Password, Username

if TYPE_CHECKING:
    from typing import Dict

    from mw_url_shortener.settings import Settings

auth_lock = asyncio.Lock()


class OAuth2PasswordBearerHandler(Auth):
    "tries to authenticate to the remote api"
    # likely won't need
    # requires_request_body = True
    requires_response_body = True

    def __init__(
        self,
        settings: "Settings",
        token: Optional[str] = None,
        username: Optional[Username] = None,
        password: Optional[Password] = None,
    ):
        self.oauth2_endpoint_url = f"{settings.api_base_url}/v0/security/token"
        self.token = token
        self.username = username
        self.password = password
        self.no_credentials = not ((username and password) or token)

    @property
    def authorization_headers(self) -> AuthorizationHeaders:
        assert self.token is not None, "missing authentication token"
        return make_authorization_headers(token=self.token)

    def need_authentication(self, response: Response) -> bool:
        status_code = response.status_code
        assert isinstance(
            status_code, int
        ), f"expected status_code to be int, not '{type(status_code)}': '{status_code}'"
        header = response.headers.get("www-authenticate", "")  # type: ignore
        assert isinstance(
            header, str  # type: ignore
        ), f"expected header to be a str, not '{type(header)}': '{header}'"  # type: ignore
        return status_code == 401 and header == "Bearer"

    # NOTE:TEST
    # - no token, good username+password
    # - no token, bad username+password
    # - expired token, good username+password
    # - expired token, bad username+password
    # - valid token
    async def async_auth_flow(
        self, request: Request
    ) -> AsyncGenerator[Request, Response]:
        # NOTE:BUG::AUTHENTICATION this could potentially expose the token,
        # username, and password to a mistyped base_url
        if self.token is not None:
            # NOTE:TYPES httpx.Request lists the type of headers as requiring a
            # Dict, when it'd be fine with a Mapping
            # request.headers.update(authorization_headers)
            request.headers["Authorization"] = self.authorization_headers[
                "Authorization"
            ]

        response = yield request

        if not self.need_authentication(response):
            return

        # refresh token
        if not (self.username and self.password):
            raise HTTPStatusError(
                message="cannot refresh token without username and password",
                request=response.request,
                response=response,
            )

        form_data = OAuth2PasswordRequestFormData(
            username=self.username,
            password=self.password,
        )

        headers: "Dict[str, str]"
        user_agent: "Optional[str]" = request.headers.get("User-Agent", None)
        assert isinstance(
            user_agent, (str, type(None))
        ), f"expected user-agent to be a str, not '{type(user_agent)}' '{user_agent}'"
        if user_agent:
            headers = {"User-Agent": user_agent}

        # the authentication lock should be held until self.token is written
        # to, to prevent another call from checking if self.token is None, and
        # starting another refresh_token() that will wait at the auth_lock
        # until this one completes
        async with auth_lock:
            token_response = yield Request(
                method="POST",
                url=self.oauth2_endpoint_url,
                data=cast("Dict[str, str]", form_data),
                headers=headers,
            )

            status_code = token_response.status_code
            assert isinstance(
                status_code, int
            ), f"expected status_code to be int, not '{type(status_code)}': '{status_code}'"
            if status_code != 200:
                raise HTTPStatusError(
                    message="cannot refresh token",
                    request=token_response.request,
                    response=token_response,
                )

            # NOTE:3rd-party-bug::HTTPX requires_response_body is set on
            # the class, so I should be able to use token_response.text
            # instead
            token_response_data = (await token_response.aread()).decode("utf-8")
            if not token_response_data:
                raise HTTPStatusError(
                    message="no token in response",
                    request=token_response.request,
                    response=token_response,
                )

            try:
                access_token = AccessToken.parse_raw(token_response_data)  # type: ignore
            except pydantic.ValidationError as error:
                raise HTTPStatusError(
                    message="invalid token in response",
                    request=token_response.request,
                    response=token_response,
                ) from error
            self.token = access_token.access_token

        # NOTE:TYPES httpx.Request lists the type of headers as requiring a
        # Dict, when it'd be fine with a Mapping
        # request.headers.update(authorization_headers)
        request.headers["Authorization"] = self.authorization_headers["Authorization"]

        final_response = yield request

        if self.need_authentication(final_response):
            raise HTTPStatusError(
                message="cannot authenticate",
                request=final_response.request,
                response=final_response,
            )

    def sync_auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        raise RuntimeError("Cannot do authentication synchronously")
