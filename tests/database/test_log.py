"""
does the database interface for logs behave as expected?
"""
from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import log as log_interface
from mw_url_shortener.schemas.log import (
    EventType,
    Log,
    LogCreate,
    RedirectCreateEvent,
)
from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate


async def test_create_redirect_log(in_memory_database: AsyncSession) -> None:
    "can a redirect creation event be logged"
    create_redirect_schema = RedirectCreate()
    redirect_id: int = 1
    created_redirect = Redirect(id=redirect_id, **create_redirect_schema.dict())
    redirect_create_event = RedirectCreateEvent(
        actor=BuiltinActor.cli, redirect=created_redirect
    )
    create_log_schema = LogCreate(event=redirect_create_event)

    created_log = await log_interface.create(
        in_memory_database, event=create_log_schema
    )
    assert created_log
    print(created_log)
