from typing import TYPE_CHECKING, List

from pydantic import parse_raw_as

from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate

from .base import Endpoint, RemoteInterfaceBase

if TYPE_CHECKING:
    from typing import Dict, Optional

    from httpx import AsyncClient

    Params = Dict[str, str]


class UserRemoteInterface(RemoteInterfaceBase[User, UserCreate, UserUpdate]):
    async def search(
        self,
        opened_resource: "AsyncClient",
        /,
        *,
        skip: int = 0,
        limit: int = 100,
        id: "Optional[int]" = None,
        username: "Optional[str]" = None,
    ) -> "List[User]":
        params: "Params" = {
            "skip": str(skip),
            "limit": str(limit),
        }
        if id is not None:
            params["id"] = str(id)
        if username is not None:
            params["username"] = username

        response = await opened_resource.get("/v0/user/", params=params)

        user_schemas = parse_raw_as(List[User], response.text)

        return user_schemas

    async def authenticate(
        self, opened_resource: "AsyncClient", /, *, username: str, password: str
    ) -> "Optional[User]":
        params: "Params" = {"username": username, "password": password}
        response = await opened_resource.post(
            "/v0/user/check_authentication", params=params
        )
        schema_json = response.text
        if not schema_json:
            return None
        return User.parse_raw(schema_json)  # type: ignore


user = UserRemoteInterface(User, Endpoint.user)  # type: ignore
