"""
do all cli commands dealing with users work correctly?
"""
import asyncio
from functools import partial
from pathlib import Path

from click.testing import Result
from pytest import CaptureFixture
from sqlalchemy import and_, select
from typer.testing import CliRunner

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.dependency_injection import initialize_depency_injection
from mw_url_shortener.schemas.user import User

from ..utils import random_password, random_username


async def test_create_user(on_disk_database: Path, capsys: CaptureFixture) -> None:
    "can a user be created and read back?"
    test_username = random_username()
    test_password = random_password()

    def runner() -> Result:
        cli_test_client = CliRunner()

        return cli_test_client.invoke(
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

    initialize_depency_injection()
    with capsys.disabled():
        result = await asyncio.get_running_loop().run_in_executor(None, runner)
    assert result.exit_code == 0
    created_user = User.parse_raw(result.stdout)
    assert created_user
