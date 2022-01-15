from typing import Dict, List, Optional

from httpx import AsyncClient
from pydantic import parse_raw_as

from mw_url_shortener.schemas.redirect import (
    Redirect,
    RedirectCreate,
    RedirectUpdate,
    random_short_link,
)
from mw_url_shortener.settings import defaults

from .base import Endpoint, RemoteInterfaceBase


class RedirectRemoteInterface(
    RemoteInterfaceBase[Redirect, RedirectCreate, RedirectUpdate],
):
    async def search(
        self,
        opened_resource: AsyncClient,
        /,
        *,
        skip: int = 0,
        limit: int = 100,
        id: Optional[int] = None,
        short_link: Optional[str] = None,
        url: Optional[str] = None,
        response_status: Optional[int] = None,
        body: Optional[str] = None,
    ) -> List[Redirect]:
        params: Dict[str, str] = {
            "skip": str(skip),
            "limit": str(limit),
        }
        if id is not None:
            params["id"] = str(id)
        if short_link is not None:
            params["short_link"] = short_link
        if url is not None:
            params["url"] = url
        if response_status is not None:
            params["response_status"] = str(response_status)
        if body is not None:
            params["body"] = str(body)

        async with opened_resource as client:
            response = await client.get("/v0/redirect/", params=params)

        redirect_schemas = parse_raw_as(List[Redirect], response.text)

        return redirect_schemas

    async def unique_short_link(
        self,
        opened_resource: AsyncClient,
        /,
        *,
        short_link_length: int = defaults.short_link_length,
    ) -> Optional[str]:
        """
        tries to find a unique short link of the specified length

        if this method returns nothing, it might be time to either
        significantly change the short_link_characters, or change
        short_link_length
        """
        params: Dict[str, str] = {"short_link_length": str(short_link_length)}
        async with opened_resource as client:
            response = await client.get("/v0/redirect/unique_short_link", params=params)
        short_link = response.text
        if not short_link:
            return None
        return short_link


redirect = RedirectRemoteInterface(Redirect, Endpoint.redirect)  # type: ignore
