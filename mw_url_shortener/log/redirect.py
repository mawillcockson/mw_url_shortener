"""
logging interface for redirects
"""
from typing import TYPE_CHECKING

from mw_url_shortener.dependency_injection.database import get_async_sessionmaker
from mw_url_shortener.interfaces import database
from mw_url_shortener.schemas.log import LogCreate, RedirectCreateEvent

if TYPE_CHECKING:
    from mw_url_shortener.schemas.log import Actor
    from mw_url_shortener.schemas.redirect import Redirect


async def create(redirect: "Redirect", actor: "Actor") -> None:
    "logs the newly-created redirect"
    async_sessionmaker = get_async_sessionmaker()
    async with async_sessionmaker() as async_session:
        await database.log.create(
            async_session,
            create_object_schema=LogCreate(
                event=RedirectCreateEvent(redirect=redirect, actor=actor)
            ),
        )
