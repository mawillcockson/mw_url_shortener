from typing import TYPE_CHECKING

from sqlalchemy.orm import sessionmaker

from .interfaces import get_resource

if TYPE_CHECKING:
    from mw_url_shortener.database.start import AsyncSession


def get_async_sessionmaker() -> "sessionmaker[AsyncSession]":
    resource = get_resource()
    assert isinstance(resource, sessionmaker), (  # type: ignore
        "expected resource to be sessionmaker[AsyncSession], "
        f"got {type(resource)} '{resource}'"
    )
    return resource  # type: ignore[unreachable]
