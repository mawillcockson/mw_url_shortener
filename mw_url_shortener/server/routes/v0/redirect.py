from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import Response

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import redirect as redirect_interface
from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate
from mw_url_shortener.schemas.user import User

from ..dependencies import get_async_session, get_current_user


async def match_redirect(
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
        raise HTTPException(status_code=404, detail="redirect not found")

    redirect_schema = redirect_schemas[0]
    headers = {
        "Location": str(redirect_schema.url),
    }
    return Response(
        headers=headers,
        status_code=int(redirect_schema.response_status),
        content=str(redirect_schema.body),
        media_type="text/plain",
    )


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


router = APIRouter()
router.get("/match/{short_link:path}")(match_redirect)
router.post("/")(create)
