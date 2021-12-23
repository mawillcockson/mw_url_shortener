from pathlib import Path

import inject
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from mw_url_shortener.settings import Settings

from .models.base import DeclarativeBase


async def make_session(database_url: str) -> "sessionmaker[AsyncSession]":
    "creates the main way to talk to the database"
    engine = create_async_engine(database_url, echo=True, future=True)

    # Q: should the database be created if it doesn't exist?
    # A: this should be done at the client layer, using a function provided
    # here to "initialize" a database file

    async with engine.begin() as connection:
        await connection.run_sync(DeclarativeBase.metadata.create_all)  # type: ignore

    async_sessionmaker = sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)  # type: ignore
    return async_sessionmaker


def create_database_file(path: Path) -> Path:
    """
    initialize a file for use with the database engine

    will only create a new file; an existing file can be opened with
    make_session()
    """
    import sqlite3

    if path.exists():
        # raise FileExistsError(f"will not overwite already existing path: '{path}'")
        return path

    # Taken from:
    # https://github.com/kvesteri/sqlalchemy-utils/blob/b262d2d33a2ff6cb3b3dbabb25680d4686c7c18a/sqlalchemy_utils/functions/database.py#L591-L593
    with sqlite3.connect(str(path)) as connection:
        connection.execute("CREATE TABLE DB(id int);")
        connection.execute("DROP TABLE DB;")

    return path


def inject_async_session(binder: inject.Binder, *, async_session: AsyncSession) -> None:
    binder.bind(AsyncSession, async_session)
