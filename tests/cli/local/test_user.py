"""
do all cli commands dealing with users work correctly?
"""
import json
from pathlib import Path
from typing import List

import inject
import pytest

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.database.start import AsyncSession, make_sessionmaker
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.schemas.user import User
from mw_url_shortener.settings import OutputStyle, Settings
from tests.utils import random_password, random_username

from .conftest import CommandRunner


async def test_create_user(
    on_disk_database: Path,
    run_test_command: CommandRunner,
) -> None:
    "can a user be created and read back?"
    test_username = random_username()
    test_password = random_password()

    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
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
        False,
    )

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


async def test_get_by_id(
    on_disk_database: Path,
    run_test_command: CommandRunner,
) -> None:
    "can a user be retrieved by id?"
    test_username = random_username()
    test_password = random_password()

    create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
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

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_user = User.parse_raw(create_result.stdout)
    assert created_user

    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "get-by-id",
            str(created_user.id),
        ],
    )

    assert result.exit_code == 0, f"search result: {result}"
    retrieved_user = User.parse_raw(result.stdout)
    assert retrieved_user
    assert retrieved_user == created_user


@pytest.mark.xfail(reason="not implemented")
async def test_search_by_username(
    on_disk_database: Path,
    run_test_command: CommandRunner,
) -> None:
    "can a specific user be retrieved?"
    username = random_username()
    other_username = random_username()
    assert username != other_username

    password = random_password()

    first_create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "create",
            "--username",
            str(username),
            "--password",
            str(password),
        ],
    )
    assert (
        first_create_result.exit_code == 0
    ), f"first create result: {first_create_result}"
    desired_user = User.parse_raw(first_create_result.stdout)
    assert desired_user

    other_create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "create",
            "--username",
            str(other_username),
            "--password",
            str(password),
        ],
    )
    assert (
        other_create_result.exit_code == 0
    ), f"other create result: {other_create_result}"
    other_user = User.parse_raw(other_create_result.stdout)
    assert other_user != desired_user

    search_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "search",
            "--username",
            str(username),
        ],
    )
    assert search_result.exit_code == 0, f"search result: {search_result}"
    search_data = json.loads(search_result.stdout)
    assert isinstance(search_data, list), f"search data: {search_data}"

    retrieved_users: List[User] = []
    for user_data in search_data:
        user = User.parse_obj(user_data)

    assert len(retrieved_users) == 1
    assert desired_user in retrieved_users
