"""
minimal working example to reproduce the bug of the mysteriously appearing values
"""
import asyncio
from asyncio import BaseEventLoop as AsyncLoopType
from functools import partial
from pathlib import Path
from typing import Awaitable, Callable, Iterator, List

import inject
import pytest
import typer
from click.testing import Result
from pytest import CaptureFixture
from typer import Typer
from typer.testing import CliRunner

app = typer.Typer()

@app.command()
def command() -> None:
    "dummy command"


def inject_loop(binder: inject.Binder, *, loop: AsyncLoopType) -> None:
    binder.bind(AsyncLoopType, loop)


def initialize_dependency_injection(
    configurators: List[inject.BinderCallable] = [],
) -> None:
    assert len(configurators) == 0, str(configurators)
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
def anyio_backend() -> str:
    "declares the backend to use for all async tests"
    # SQLAlchemy uses a sqlite DBAPI (aiosqlite) that depends upon asyncio
    return "asyncio"


async def test_command_first_time(
    capsys: CaptureFixture[str],
    cli_test_client: CliRunner,
    anyio_backend: str,
) -> None:
    "can a user be created and read back?"
    test_command = partial(cli_test_client.invoke, app, ["--help"])
    initialize_dependency_injection()

    with capsys.disabled():
        return await asyncio.get_running_loop().run_in_executor(None, test_command)


async def test_command_second_time(
    tmp_path: Path,
    capsys: CaptureFixture[str],
    cli_test_client: CliRunner,
    anyio_backend: str,
) -> None:
    "is the database path accepted as a command-line parameter?"
    database_path = tmp_path / "temporary_database.sqlite"

    test_command = partial(cli_test_client.invoke, app, ["--help"])
    initialize_dependency_injection()

    with capsys.disabled():
        return await asyncio.get_running_loop().run_in_executor(None, test_command)
