from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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
