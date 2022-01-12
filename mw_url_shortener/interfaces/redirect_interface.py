from typing import List, Optional, Protocol, runtime_checkable

from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate, RedirectUpdate

from .base import ContravariantOpenedResourceT, InterfaceBaseProtocol


@runtime_checkable
class RedirectInterface(
    InterfaceBaseProtocol[
        ContravariantOpenedResourceT, Redirect, RedirectCreate, RedirectUpdate
    ],
    Protocol[ContravariantOpenedResourceT],
):
    "generic redirect data interface"

    async def search(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        skip: int = 0,
        limit: int = 0,
        short_link: Optional[str] = None,
        url: Optional[str] = None,
        response_status: Optional[int] = None,
        body: Optional[str] = None,
    ) -> List[Redirect]:
        ...

    async def get_by_short_link(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        short_link: str,
    ) -> Optional[Redirect]:
        ...

    async def unique_short_link(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        short_link_length: int,
    ) -> Optional[str]:
        ...
