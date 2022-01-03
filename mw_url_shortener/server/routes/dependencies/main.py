# mypy: allow_any_expr
from typing import AsyncIterator

import inject
from fastapi import Depends

from mw_url_shortener.database.start import AsyncSession, make_sessionmaker
from mw_url_shortener.server.settings import ServerSettings


async def get_server_settings() -> ServerSettings:
    return inject.instance(ServerSettings)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    server_settings = await get_server_settings()
    async_sessionmaker = await make_sessionmaker(
        server_settings.database_url, echo=server_settings.log_db_access
    )
    async with async_sessionmaker() as async_session:
        yield async_session
