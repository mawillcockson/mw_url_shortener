"""
can the app take all of it's configuration through command line parameters?
"""
from pathlib import Path

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.settings import OutputStyle, Settings, defaults

from .conftest import TestCommandRunner


async def test_database_path(
    tmp_path: Path,
    run_test_command: TestCommandRunner,
) -> None:
    "is the database path accepted as a command-line parameter?"
    database_path = tmp_path / "temporary_database.sqlite"

    result = await run_test_command(
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

    assert result.exit_code == 0, f"result: {result}"

    expected_settings = defaults.copy(update={"database_path": str(database_path)})
    settings = Settings.parse_raw(result.stdout)
    assert settings == expected_settings

    # make sure no local files were modified
    assert not database_path.exists()