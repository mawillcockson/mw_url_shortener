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


class Settings:
    "dummy substitute"


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


async def test_command_first_time(
    run_test_command: TestCommandRunner,
) -> None:
    "can a user be created and read back?"

    result = await run_test_command(app, [])


async def test_command_second_time(
    tmp_path: Path,
    run_test_command: TestCommandRunner,
) -> None:
    "is the database path accepted as a command-line parameter?"
    database_path = tmp_path / "temporary_database.sqlite"

    result = await run_test_command(app, [])
