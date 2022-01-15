# mypy: allow_any_expr
from typing import Any, Dict, List, Optional, Union

from httpx import AsyncClient
from pydantic import parse_raw_as

from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
from mw_url_shortener.security import hash_password, verify_password

from ..user_interface import UserInterface
from .base import RemoteInterfaceBase


class UserRemoteInterface(
    RemoteInterfaceBase[User, UserCreate, UserUpdate], UserInterface[AsyncClient]
):
    async def search(
        self,
        opened_resource: AsyncClient,
        /,
        *,
        skip: int = 0,
        limit: int = 100,
        id: Optional[int] = None,
        username: Optional[str] = None,
    ) -> List[User]:
        params: "Dict[str, str]" = {
            "skip": str(skip),
            "limit": str(limit),
        }
        if id is not None:
            params["id"] = str(id)
        if username is not None:
            params["username"] = username

        async with opened_resource as client:
            response = await client.get("/v0/user/", params=params)

        user_schemas = parse_raw_as(List[User], response.text)

        return user_schemas


user = UserRemoteInterface(User)
