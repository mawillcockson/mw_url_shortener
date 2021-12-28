"""
minimal working example to reproduce the bug of the mysteriously appearing values
"""
import asyncio
import sqlite3
from functools import partial
from pathlib import Path
from typing import AsyncIterator, Awaitable, Callable, Iterator, List

import inject
import pytest
from click.testing import Result
from pytest import CaptureFixture
from sqlalchemy.ext.asyncio import AsyncSession
from typer import Typer
from typer.testing import CliRunner

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.database.start import AsyncSession, make_sessionmaker
from mw_url_shortener.dependency_injection import initialize_dependency_injection
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.schemas.user import User
from mw_url_shortener.settings import OutputStyle, Settings, defaults


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


async def test_create_user(
    on_disk_database: Path,
    run_test_command: TestCommandRunner,
) -> None:
    "can a user be created and read back?"

    result = await run_test_command(
        app,
        [
            "--output-style=json",
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "create",
            "--username",
            "test",
            "--password",
            "test",
        ],
    )

    assert result.exit_code == 0, f"result: {result}"
    created_user = User.parse_raw(result.stdout)
    assert created_user

    # I think this uses too many of the implementation details, but I also
    # think it's maybe okay to do, to confirm that the correct database is
    # being used
    settings = inject.instance(Settings)
    database_url_end = settings.database_url_joiner + str(on_disk_database)
    assert settings.database_url.endswith(database_url_end)
    async_sessionmaker = await make_sessionmaker(settings.database_url)
    async with async_sessionmaker() as async_session:
        retrieved_user = await database_interface.user.get_by_id(
            async_session, id=created_user.id
        )
    assert retrieved_user == created_user


async def test_database_path(
    tmp_path: Path,
    run_test_command: TestCommandRunner,
) -> None:
    "is the database path accepted as a command-line parameter?"
    database_path = tmp_path / "temporary_database.sqlite"

    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(database_path),
            "show-configuration",
        ],
    )

    assert result.exit_code == 0, f"result: {result}"

    expected_settings = defaults.copy(update={"database_path": str(database_path)})
    settings = Settings.parse_raw(result.stdout)
    assert settings == expected_settings

    # make sure no local files were modified
    assert not database_path.exists()
