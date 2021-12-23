"""
can the app take all of it's configuration through command line parameters?
"""
from pathlib import Path

from typer.testing import CliRunner

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.settings import Settings


def test_database_path(tmp_path: Path, cli_test_client: CliRunner) -> None:
    "is the database path accepted as a command-line parameter?"
    database_path = tmp_path / "temporary_database.sqlite"

    result = cli_test_client.invoke(
        app, ["--database-path", str(database_path), "show-configuration", "--json"]
    )
    assert result.exit_code == 0

    settings = Settings.parse_raw(result.stdout)
    assert settings.database_path == database_path
