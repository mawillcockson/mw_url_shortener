from typing import AsyncIterator

import pytest
from typer.testing import CliRunner

from mw_url_shortener.dependency_injection import initialize_depency_injection


@pytest.fixture
async def cli_test_client(anyio_backend: str) -> AsyncIterator[CliRunner]:
    inject.clear()
    initialize_depency_injection()
    yield CliRunner()
    inject.clear()
