from typing import TYPE_CHECKING

from fastapi import Depends

from mw_url_shortener.database.start import make_sessionmaker

from ..settings import ServerSettings

if TYPE_CHECKING:
    from typing import AsyncIterator, Optional

    from mw_url_shortener.database.start import AsyncSession


async def get_async_session() -> "AsyncIterator[AsyncSession]":
    settings = ServerSettings()
    async_sessionmaker = await make_sessionmaker(settings.database_url)
    async with async_sessionmaker() as async_session:
        yield async_session
