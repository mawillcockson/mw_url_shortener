from typing import Iterator

import inject
import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_test_client() -> Iterator[CliRunner]:
    inject.clear()
    yield CliRunner()
    inject.clear()
