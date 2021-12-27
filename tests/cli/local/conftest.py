import asyncio
from typing import Awaitable, Callable, Iterator

import inject
import pytest
from click.testing import Result as Result
from pytest import CaptureFixture
from typer.testing import CliRunner

from mw_url_shortener.dependency_injection import initialize_depency_injection


@pytest.fixture
def cli_test_client() -> Iterator[CliRunner]:
    inject.clear()
    yield CliRunner()
    inject.clear()


TestCommand = Callable[[], Result]


@pytest.fixture
def run_test_command(
    capsys: CaptureFixture[str],
) -> Callable[[TestCommand], Awaitable[Result]]:
    async def runner(test_command: TestCommand) -> Result:
        initialize_depency_injection()

        with capsys.disabled():
            return await asyncio.get_running_loop().run_in_executor(None, test_command)

    return runner
