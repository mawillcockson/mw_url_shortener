from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models.registry import mapper_registry


async def make_session(database_url: str) -> AsyncSession:
    "creates the main way to talk to the database"
    engine = create_async_engine(database_url, echo=True, future=True)

    # Q: should the database be created if it doesn't exist?
    # A: this should be done at the client layer, using a function provided
    # here to "initialize" a database file

    async with engine.begin() as connection:
        await connection.run_sync(mapper_registry.metadata.create_all)

    return sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)


async def close_session(session: AsyncSession) -> None:
    """
    a reminder that, if AsyncSession isn't used inside an async with
    statement, this method should be called to perform cleanup

    hopefully doesn't have to be used
    """
    await session.dispose()
