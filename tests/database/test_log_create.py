"""
are logs created for all the database actions, and can those logs be retrieved?
"""
from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import log as log_interface
from mw_url_shortener.interfaces.database import redirect as redirect_interface
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.log import EventType, Log, LogCreate, LogUpdate
from mw_url_shortener.schemas.redirect import RedirectCreate
from mw_url_shortener.schemas.user import UserCreate


async def test_create_redirect_log(in_memory_database: AsyncSession) -> None:
    "is a log created upon redirect creation?"
    create_redirect_schema = RedirectCreate()

    created_redirect = await redirect_interface.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )
    assert created_redirect

    creation_logs = await log_interface.search(
        in_memory_database, event_type=EventType.redirect_create
    )
    assert creation_logs
    assert len(creation_logs) == 1, f"{creation_logs}"


async def test_create_redirect_defaults(in_memory_database: AsyncSession) -> None:
    "if no values are provided, is a redirected created with default values?"
    create_redirect_schema = RedirectCreate()

    created_redirect = await redirect_interface.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )
    assert created_redirect

    creation_logs = await log_interface.search(
        in_memory_database, event_type=EventType.redirect_create
    )
    assert creation_logs
    assert len(creation_logs) == 1, f"{creation_logs}"
