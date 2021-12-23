import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_test_client() -> CliRunner:
    return CliRunner()
