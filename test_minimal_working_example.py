"""
minimal working example to reproduce the bug of the mysteriously appearing values
"""
import asyncio
import sqlite3
from asyncio import BaseEventLoop as AsyncLoopType
from functools import partial
from pathlib import Path
from typing import AsyncIterator, Awaitable, Callable, Iterator, List

import typer
import inject
import pytest
from click.testing import Result
from pytest import CaptureFixture
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typer import Typer
from typer.testing import CliRunner

from mw_url_shortener.database.models.base import DeclarativeBase
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.settings import Settings

app = typer.Typer()


@app.callback()
def callback(ctx: typer.Context) -> None:
    if ctx.resilient_parsing or ctx.invoked_subcommand is None:
        return

    loop = inject.instance(AsyncLoopType)
    async_sessionmaker = asyncio.run_coroutine_threadsafe(
        make_sessionmaker(settings.database_url), loop=loop
    ).result()
    async_sessionmaker_injector = partial(
        inject_async_sessionmaker, async_sessionmaker=async_sessionmaker
    )

    reconfigure_dependency_injection([async_sessionmaker_injector])


@app.command()
def create() -> None:
    async_sessionmaker = inject.instance("sessionmaker[AsyncSession]")
    with open_resource(async_sessionmaker) as opened_resource:
        created_user = run_sync(
            database_interface.user.create(
                opened_resource, create_object_schema=create_user_schema
            )
        )


@app.command()
def show() -> None:
    settings = inject.instance(Settings)
    typer.echo(settings.json())


async def make_sessionmaker(database_url: str) -> "sessionmaker[AsyncSession]":
    "creates the main way to talk to the database"
    engine = create_async_engine(database_url, echo=True, future=True)

    # Q: should the database be created if it doesn't exist?
    # A: this should be done at the client layer, using a function provided
    # here to "initialize" a database file

    async with engine.begin() as connection:
        await connection.run_sync(DeclarativeBase.metadata.create_all)  # type: ignore

    async_sessionmaker = sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)  # type: ignore
    return async_sessionmaker


def inject_async_sessionmaker(
    binder: inject.Binder, *, async_sessionmaker: "sessionmaker[AsyncSession]"
) -> None:
    binder.bind("sessionmaker[AsyncSession]", async_sessionmaker)


def inject_settings(binder: inject.Binder, *, settings: Settings) -> None:
    binder.bind(Settings, settings)


def inject_loop(binder: inject.Binder, *, loop: AsyncLoopType) -> None:
    binder.bind(AsyncLoopType, loop)


def initialize_dependency_injection(
    configurators: List[inject.BinderCallable] = [],
) -> None:
    assert len(configurators) == 0, str(configurators)
    settings = Settings()
    configurators.append(partial(inject_settings, settings=settings))

    loop = asyncio.get_running_loop()
    configurators.append(partial(inject_loop, loop=loop))

    def config(binder: inject.Binder) -> None:
        for configurator in configurators:
            binder.install(configurator)

    inject.configure(config)


@pytest.fixture
def cli_test_client() -> Iterator[CliRunner]:
    inject.clear()
    yield CliRunner()
    inject.clear()


TestCommandRunner = Callable[[Typer, List[str]], Awaitable[Result]]


@pytest.fixture
async def run_test_command(
    capsys: CaptureFixture[str],
    cli_test_client: CliRunner,
    anyio_backend: str,
) -> TestCommandRunner:
    async def runner(app: Typer, arguments: List[str]) -> Result:
        test_command = partial(cli_test_client.invoke, app, arguments)
        initialize_dependency_injection()

        with capsys.disabled():
            return await asyncio.get_running_loop().run_in_executor(None, test_command)

    return runner


@pytest.fixture
def anyio_backend() -> str:
    "declares the backend to use for all async tests"
    # SQLAlchemy uses a sqlite DBAPI (aiosqlite) that depends upon asyncio
    return "asyncio"


@pytest.fixture
async def on_disk_database(tmp_path: Path, anyio_backend: str) -> Path:
    tmp_db = tmp_path / "on_disk_database"
    _ = await make_sessionmaker("sqlite+aiosqlite:///" + str(tmp_db))
    return tmp_db


async def test_command1(
    on_disk_database: Path,
    run_test_command: TestCommandRunner,
) -> None:
    "can a user be created and read back?"

    result = await run_test_command(
        app,
        ["command2"],
    )

    assert result.exit_code == 0, f"result: {result}"


async def test_command2(
    tmp_path: Path,
    run_test_command: TestCommandRunner,
) -> None:
    "is the database path accepted as a command-line parameter?"
    database_path = tmp_path / "temporary_database.sqlite"

    result = await run_test_command(
        app,
        ["command2"],
    )
