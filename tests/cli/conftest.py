import asyncio
from functools import partial
from typing import Awaitable, Callable, Iterator, List, Protocol

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
    try:
        yield CliRunner()
    finally:
        inject.clear()


class CommandRunner(Protocol):
    "from: https://stackoverflow.com/a/68392079"

    def __call__(
        self, app: Typer, arguments: List[str], clear_injection: bool = True, /
    ) -> Awaitable[Result]:
        ...


@pytest.fixture
async def run_test_command(
    capsys: CaptureFixture[str],
    cli_test_client: CliRunner,
    anyio_backend: str,
) -> CommandRunner:
    async def runner(
        app: Typer, arguments: List[str], clear_injection: bool = True
    ) -> Result:
        test_command = partial(cli_test_client.invoke, app, arguments)
        initialize_dependency_injection()

        with capsys.disabled():
            result = await asyncio.get_running_loop().run_in_executor(
                None, test_command
            )

        if clear_injection:
            inject.clear()
        return result

    return runner
