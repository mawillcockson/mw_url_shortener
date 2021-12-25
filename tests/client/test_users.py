"""
do all cli commands dealing with users work correctly?
"""
import asyncio
from pathlib import Path

from sqlalchemy import and_, select
from typer.testing import CliRunner

from mw_url_shortener.cli.entry_point import app

from ..utils import random_password, random_username


async def test_create_user(on_disk_database: Path, cli_test_client: CliRunner) -> None:
    "can a user be created and read back?"
    test_username = random_username()
    test_password = random_password()

    result = await asyncio.get_running_loop().run_in_executor(
        None,
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
    assert result.exit_code == 0
    assert (
        f"user '{test_username}' created with id '{expected_user_id}'" in result.stdout
    )

    retrieved_user = await database_interface.user.get_by_id()
