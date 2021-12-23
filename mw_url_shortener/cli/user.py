"the 'user' subcommand of the client"
import inject
import typer

from mw_url_shortener.settings import Settings
from asyncio import BaseEventLoop as AsyncLoopType
import asyncio
from mw_url_shortener.database_interface import user
from mw_url_shortener.dependency_injection import reconfigure_dependency_injection
from mw_url_shortener.database.start import make_session, inject_async_session
from mw_url_shortener.schemas.user import UserCreate, User
from sqlalchemy.ext.asyncio import AsyncSession

app = typer.Typer()


@app.command()
def create(
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
) -> None:
    create_user_schema = UserCreate(username=username, password=password)
    settings = inject.instance(Settings)
    loop = inject.instance(AsyncLoopType)
    async_session = inject.instance(AsyncSession)

    async def call() -> User:
        async with async_session() as session:
            return await user.create(session, create_object_schema=create_user_schema)

    created_user = asyncio.run_coroutine_threadsafe(call(), loop=loop).result()

    # if settings.print_json:
    if True:
        typer.echo(created_user.json())

    # # should instead use python-inject in the database_interface to provide
    # # AsyncSession, and pass the async_session_awaitable as the first task to
    # # run in a queue, and then the awaitable that performs the user creation as
    # # the second task
    # async def wrapper(async_session_awaitable: "Awaitable[AsyncSession]", func) -> None:
    #     async_session = await async_session_awaitable
    #     return await func(async_session_awaitable)


# update
# remove_by_id
# search
