"""
do all cli commands dealing with users work correctly?
"""
from functools import partial
from pathlib import Path
from typing import Callable

import inject
from click.testing import Result
from typer.testing import CliRunner

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.database.start import AsyncSession, make_sessionmaker
from mw_url_shortener.interfaces import Resource
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.schemas.user import User
from mw_url_shortener.settings import Settings

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

    result = await run_test_command(test_command)
    assert result.exit_code == 0, f"result: {result}"
    created_user = User.parse_raw(result.stdout)
    assert created_user

    # I think this uses too many of the implementation details, but I also
    # think it's maybe okay to do, to confirm that the correct database is
    # being used
    settings = inject.instance(Settings)
    database_url_end = settings.database_url_joiner + str(on_disk_database)
    assert settings.database_url.endswith(database_url_end)
    async_sessionmaker = await make_sessionmaker(settings.database_url)
    async with async_sessionmaker() as async_session:
        retrieved_user = await database_interface.user.get_by_id(
            async_session, id=created_user.id
        )
    assert retrieved_user == created_user
