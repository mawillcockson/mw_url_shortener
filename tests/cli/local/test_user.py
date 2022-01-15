"""
do all cli commands dealing with users work correctly?
"""
import json
from pathlib import Path
from typing import List

import inject
import pytest
from pydantic import parse_raw_as

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
        retrieved_users = await database_interface.user.search(
            async_session, id=created_user.id
        )
    assert created_user in retrieved_users
    assert len(retrieved_users) == 1

    inject.clear()


async def test_search_by_id(
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
            "search",
            "--id",
            str(created_user.id),
        ],
    )

    assert result.exit_code == 0, f"search result: {result}"
    retrieved_users = parse_raw_as(List[User], result.stdout)
    assert created_user in retrieved_users
    assert len(retrieved_users) == 1


async def test_search_non_existent_user(
    on_disk_database: Path,
    run_test_command: CommandRunner,
) -> None:
    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "search",
            "--id",
            str(0),
        ],
    )

    assert result.exit_code == 1, f"search result: {result}"


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
    retrieved_users: List[User] = parse_raw_as(List[User], search_result.stdout)
    assert len(retrieved_users) == 1
    assert desired_user in retrieved_users


async def test_remove_by_id(
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
            "remove-by-id",
            str(created_user.id),
        ],
    )

    assert result.exit_code == 0, f"search result: {result}"
    removed_user = User.parse_raw(result.stdout)
    assert removed_user
    assert removed_user == created_user


async def test_authentication(
    on_disk_database: Path, run_test_command: CommandRunner
) -> None:
    """
    if a user is in the database, does the cli correctly identify if the info
    matches?
    """
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
            "check-authentication",
            "--username",
            str(test_username),
            "--password",
            str(test_password),
        ],
    )

    assert result.exit_code == 0, f"search result: {result}"
    valid_user = User.parse_raw(result.stdout)
    assert valid_user
    assert valid_user == created_user


async def test_authentication_invalid_info(
    on_disk_database: Path, run_test_command: CommandRunner
) -> None:
    """
    if a user is in the database, does the cli correctly identify if the info
    matches?
    """
    test_username = random_username()

    test_password = random_password()
    incorrect_password = random_password()
    assert incorrect_password != test_password

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
            str(test_username),
            "--password",
            str(test_password),
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
            "check-authentication",
            "--username",
            str(test_username),
            "--password",
            str(incorrect_password),
        ],
    )

    assert result.exit_code == 1, f"search result: {result}"


async def test_update_all(
    on_disk_database: Path, run_test_command: CommandRunner
) -> None:
    "can all user info be modified?"
    username = random_username()
    new_username = random_username()
    assert new_username != username

    password = random_password()
    new_password = random_password()
    assert new_password != password

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
            str(username),
            "--password",
            str(password),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_user = User.parse_raw(create_result.stdout)
    assert created_user

    update_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "update-by-id",
            str(created_user.id),
            "--username",
            str(new_username),
            "--password",
            str(new_password),
        ],
    )

    assert update_result.exit_code == 0, f"search result: {update_result}"
    updated_user = User.parse_raw(update_result.stdout)
    assert updated_user
    assert updated_user.username == new_username

    authentication_failure_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "check-authentication",
            "--username",
            str(username),
            "--password",
            str(password),
        ],
    )

    assert (
        authentication_failure_result.exit_code == 1
    ), f"bad authentication success: {authentication_failure_result}"

    authentication_failure_result2 = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "check-authentication",
            "--username",
            str(new_username),
            "--password",
            str(password),
        ],
    )

    assert (
        authentication_failure_result2.exit_code == 1
    ), f"bad authentication success: {authentication_failure_result2}"

    authentication_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "check-authentication",
            "--username",
            str(new_username),
            "--password",
            str(new_password),
        ],
    )

    assert (
        authentication_result.exit_code == 0
    ), f"authentication failure: {authentication_result}"
    authenticated_user = User.parse_raw(authentication_result.stdout)
    assert authenticated_user
    assert authenticated_user == updated_user


async def test_update_password(
    on_disk_database: Path, run_test_command: CommandRunner
) -> None:
    "if only the password is updated, does all other info remain the same?"
    username = random_username()

    password = random_password()
    new_password = random_password()
    assert new_password != password

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
            str(username),
            "--password",
            str(password),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_user = User.parse_raw(create_result.stdout)
    assert created_user

    update_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "update-by-id",
            str(created_user.id),
            "--password",
            str(new_password),
        ],
    )

    assert update_result.exit_code == 0, f"search result: {update_result}"
    updated_user = User.parse_raw(update_result.stdout)
    assert updated_user
    assert updated_user.username == username

    authentication_failure_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "check-authentication",
            "--username",
            str(username),
            "--password",
            str(password),
        ],
    )

    assert (
        authentication_failure_result.exit_code == 1
    ), f"bad authentication success: {authentication_failure_result}"

    authentication_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "check-authentication",
            "--username",
            str(username),
            "--password",
            str(new_password),
        ],
    )

    assert (
        authentication_result.exit_code == 0
    ), f"authentication failure: {authentication_result}"
    authenticated_user = User.parse_raw(authentication_result.stdout)
    assert authenticated_user
    assert authenticated_user == updated_user


async def test_update_none(
    on_disk_database: Path, run_test_command: CommandRunner
) -> None:
    "if nothing is updated, will the same info be returned?"
    username = random_username()
    password = random_password()

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
            str(username),
            "--password",
            str(password),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_user = User.parse_raw(create_result.stdout)
    assert created_user

    update_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "update-by-id",
            str(created_user.id),
        ],
    )

    assert update_result.exit_code == 0, f"search result: {update_result}"
    updated_user = User.parse_raw(update_result.stdout)
    assert updated_user
    assert updated_user == created_user

    authentication_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "user",
            "check-authentication",
            "--username",
            str(username),
            "--password",
            str(password),
        ],
    )

    assert (
        authentication_result.exit_code == 0
    ), f"authentication failure: {authentication_result}"
    authenticated_user = User.parse_raw(authentication_result.stdout)
    assert authenticated_user
    assert authenticated_user == updated_user
