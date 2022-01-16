from typing import Dict, List, Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import Response

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import redirect as redirect_interface
from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate, RedirectUpdate
from mw_url_shortener.schemas.user import User
from mw_url_shortener.settings import defaults

from ..dependencies import get_async_session, get_current_user


# NOTE:TEST in client
async def unique_short_link(
    short_link_length: int = defaults.short_link_length,
    async_session: AsyncSession = Depends(get_async_session),
) -> Optional[str]:
    """
    tries to find a unique short link of the specified length

    if this method returns nothing, it might be time to either
    significantly change the short_link_characters, or change
    short_link_length
    """
    short_link = await redirect_interface.unique_short_link(
        async_session, short_link_length=short_link_length
    )
    return short_link


async def match(
    request: Request,
    short_link: str,
    async_session: AsyncSession = Depends(get_async_session),
) -> Response:
    """
    return a redirect that matches the short link

    any characters are valid in the resource path, including `/`
    """
    redirect_schemas = await redirect_interface.search(
        async_session, short_link=short_link
    )
    if len(redirect_schemas) != 1:
        # this could say "too many matching redirects", but this method can be
        # called by anyone, and I wouldn't want to give that away to someone
        # who isn't logged in
        raise HTTPException(status_code=404, detail="redirect not found")

    redirect_schema = redirect_schemas[0]
    headers: "Dict[str, str]" = {}
    if redirect_schema.url:
        # from:
        # https://github.com/encode/starlette/blob/a7c5a41396752c39a5a9b688e2dccfaca152a62f/starlette/responses.py#L198
        url = quote(str(redirect_schema.url), safe=":/%#?=@[]!$&'()*+,;")
        headers["Location"] = url
    return Response(
        headers=headers,
        status_code=int(redirect_schema.response_status),
        content=str(redirect_schema.body),
        media_type="text/plain",
    )


async def search(
    skip: int = 0,
    limit: int = 100,
    id: Optional[int] = None,
    short_link: Optional[str] = None,
    url: Optional[str] = None,
    response_status: Optional[int] = None,
    body: Optional[str] = None,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> List[Redirect]:
    retrieved_users = await redirect_interface.search(
        async_session,
        skip=skip,
        limit=limit,
        id=id,
        short_link=short_link,
        url=url,
        response_status=response_status,
        body=body,
    )
    return retrieved_users


async def create(
    create_object_schema: RedirectCreate,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Redirect:
    created_redirect = await redirect_interface.create(
        async_session, create_object_schema=create_object_schema
    )
    if created_redirect is not None:
        return created_redirect

    raise HTTPException(status_code=409, detail="could not create redirect")


async def update(
    current_object_schema: Redirect,
    update_object_schema: RedirectUpdate,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Redirect:
    updated_redirect = await redirect_interface.update(
        async_session,
        current_object_schema=current_object_schema,
        update_object_schema=update_object_schema,
    )
    if updated_redirect is not None:
        return updated_redirect

    raise HTTPException(status_code=409, detail="could not update redirect")


async def remove(
    id: int,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Redirect:
    removed_redirect = await redirect_interface.remove_by_id(async_session, id=id)
    if removed_redirect is not None:
        return removed_redirect

    raise HTTPException(status_code=404, detail="could not remove redirect")


router = APIRouter()
router.get("/unique_short_link")(unique_short_link)
router.get("/match/{short_link:path}")(match)
router.get("/")(search)
router.post("/")(create)
router.put("/")(update)
router.delete("/")(remove)
