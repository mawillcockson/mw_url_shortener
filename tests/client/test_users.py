"""
do all cli commands dealing with users work correctly?
"""
from functools import partial
from pathlib import Path
from typing import Callable

from click.testing import Result
from typer.testing import CliRunner

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.schemas.user import User

from ..utils import random_password, random_username
from .conftest import Result, TestCommand


async def test_create_user(
    on_disk_database: Path,
    run_test_command: Callable[[TestCommand], Result],
    cli_test_client: CliRunner,
) -> None:
    "can a user be created and read back?"
    test_username = random_username()
    test_password = random_password()

    test_command = partial(
        cli_test_client.invoke,
        app,
        [
            "--output-style=json",
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "create",
            "--username",
            test_username,
            "--password",
            test_password,
        ],
    )

    initial_database_size = on_disk_database.stat().st_size

    result = await run_test_command(test_command)
    assert result.exit_code == 0
    created_user = User.parse_raw(result.stdout)
    assert created_user
    # assert the database was used?
    assert on_disk_database.stat().st_size > initial_database_size
