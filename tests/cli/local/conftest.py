import asyncio
from functools import partial
from typing import Awaitable, Callable, Iterator, List

import inject
import pytest
from click.testing import Result
from pytest import CaptureFixture
from typer import Typer
from typer.testing import CliRunner

from mw_url_shortener.dependency_injection import initialize_dependency_injection


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
