"""
can the app take all of it's configuration through command line parameters?
"""
from pathlib import Path

from typer.testing import CliRunner

from mw_url_shortener.cli.entry_point import OutputStyle, app
from mw_url_shortener.settings import Settings
from typing import Callable
from click.testing import Result
from functools import partial


async def test_database_path(tmp_path: Path,
    run_test_command: Callable[[TestCommand], Result],
    cli_test_client: CliRunner,
        ) -> None:
    "is the database path accepted as a command-line parameter?"
    database_path = tmp_path / "temporary_database.sqlite"

    test_command = partial(cli_test_client.invoke,
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

    result = await run_test_command(test_command)
    assert result.exit_code == 0

    settings = Settings.parse_raw(result.stdout)
    assert settings.database_path == database_path
