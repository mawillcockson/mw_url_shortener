"""
do all cli commands dealing with redirects work correctly?
"""
import json
from pathlib import Path
from typing import List

import inject
import pytest
from pydantic import parse_raw_as

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.database.start import AsyncSession, make_sessionmaker
from mw_url_shortener.dependency_injection import get_settings
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.schemas.redirect import Redirect, random_short_link
from mw_url_shortener.settings import OutputStyle, Settings, defaults
from mw_url_shortener.utils import unsafe_random_string

from .conftest import CommandRunner


async def test_create_redirect_defaults(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "can a redirect be created and read back?"
    url = defaults.redirect_url
    short_link = random_short_link(test_string_length)

    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            url,
            short_link,
        ],
        False,
    )

    assert result.exit_code == 0, f"result: {result}"
    created_redirect = Redirect.parse_raw(result.stdout)
    assert created_redirect

    # I think this uses too many of the implementation details, but I also
    # think it's maybe okay to do, to confirm that the correct database is
    # being used
    settings = get_settings()
    database_url_end = settings.database_url_joiner + str(on_disk_database)
    assert settings.database_url.endswith(database_url_end)
    async_sessionmaker = await make_sessionmaker(settings.database_url)
    async with async_sessionmaker() as async_session:
        retrieved_redirect = await database_interface.redirect.get_by_id(
            async_session, id=created_redirect.id
        )
    assert retrieved_redirect == created_redirect

    inject.clear()


async def test_create_redirect(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "can a redirect be created and read back?"
    url = unsafe_random_string(test_string_length)
    short_link = random_short_link(test_string_length)
    response_status = int(test_string_length)
    body = unsafe_random_string(test_string_length)

    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link),
            "--response-status",
            str(response_status),
            "--body",
            str(body),
        ],
    )

    assert result.exit_code == 0, f"result: {result}"
    created_redirect = Redirect.parse_raw(result.stdout)
    assert created_redirect
    assert created_redirect.url == url
    assert created_redirect.short_link == short_link
    assert created_redirect.response_status == response_status
    assert created_redirect.body == body


async def test_get_by_id(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "can a redirect be retrieved by id?"
    url = unsafe_random_string(test_string_length)
    short_link = random_short_link(test_string_length)
    response_status = int(test_string_length)
    body = unsafe_random_string(test_string_length)

    create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link),
            "--response-status",
            str(response_status),
            "--body",
            str(body),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_redirect = Redirect.parse_raw(create_result.stdout)
    assert created_redirect

    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "get-by-id",
            str(created_redirect.id),
        ],
    )

    assert result.exit_code == 0, f"search result: {result}"
    retrieved_redirect = Redirect.parse_raw(result.stdout)
    assert retrieved_redirect
    assert retrieved_redirect == created_redirect


async def test_get_non_existent_redirect(
    on_disk_database: Path,
    run_test_command: CommandRunner,
) -> None:
    "does the app exit with an error if there's no redirect to retrieve?"
    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "get-by-id",
            str(1),
        ],
    )

    assert result.exit_code == 1, f"search result: {result}"


async def test_search_by_body(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "will all redirects matching the search criteria be returned?"
    url = unsafe_random_string(test_string_length)

    short_link1 = random_short_link(test_string_length)
    short_link2 = random_short_link(test_string_length)
    short_link3 = random_short_link(test_string_length)
    assert len({short_link1, short_link2, short_link3}) == 3

    response_status = int(test_string_length)

    desired_body = unsafe_random_string(test_string_length)
    other_body = unsafe_random_string(test_string_length)
    assert desired_body != other_body

    first_desired_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link1),
            "--response-status",
            str(response_status),
            "--body",
            str(desired_body),
        ],
    )
    assert (
        first_desired_result.exit_code == 0
    ), f"first desired result: {first_desired_result}"
    first_desired_redirect = Redirect.parse_raw(first_desired_result.stdout)
    assert first_desired_redirect

    second_desired_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link2),
            "--response-status",
            str(response_status),
            "--body",
            str(desired_body),
        ],
    )
    assert (
        second_desired_result.exit_code == 0
    ), f"second desired result: {second_desired_result}"
    second_desired_redirect = Redirect.parse_raw(second_desired_result.stdout)
    assert second_desired_redirect

    other_create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link3),
            "--response-status",
            str(response_status),
            "--body",
            str(other_body),
        ],
    )
    assert (
        other_create_result.exit_code == 0
    ), f"other create result: {other_create_result}"
    other_redirect = Redirect.parse_raw(other_create_result.stdout)
    assert other_redirect not in [first_desired_redirect, second_desired_redirect]

    search_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "search",
            "--body",
            str(desired_body),
        ],
    )
    assert search_result.exit_code == 0, f"search result: {search_result}"
    retrieved_redirects: List[Redirect] = parse_raw_as(
        List[Redirect], search_result.stdout
    )
    assert len(retrieved_redirects) == 2
    assert first_desired_redirect in retrieved_redirects
    assert second_desired_redirect in retrieved_redirects


async def test_remove_by_id(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "can a redirect be removed by id?"
    url = unsafe_random_string(test_string_length)
    short_link = random_short_link(test_string_length)
    response_status = int(test_string_length)
    body = unsafe_random_string(test_string_length)

    create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link),
            "--response-status",
            str(response_status),
            "--body",
            str(body),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_redirect = Redirect.parse_raw(create_result.stdout)
    assert created_redirect

    result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "remove-by-id",
            str(created_redirect.id),
        ],
    )

    assert result.exit_code == 0, f"search result: {result}"
    removed_redirect = Redirect.parse_raw(result.stdout)
    assert removed_redirect
    assert removed_redirect == created_redirect


async def test_update_all(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "can all redirect info be modified?"
    url = unsafe_random_string(test_string_length)
    new_url = unsafe_random_string(test_string_length)
    assert new_url != url

    short_link = random_short_link(test_string_length)
    new_short_link = random_short_link(test_string_length)
    assert new_short_link != short_link

    response_status = int(test_string_length)
    new_response_status = abs(response_status + 1)
    assert new_response_status != response_status

    body = unsafe_random_string(test_string_length)
    new_body = unsafe_random_string(test_string_length)
    assert new_body != body

    create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link),
            "--response-status",
            str(response_status),
            "--body",
            str(body),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_redirect = Redirect.parse_raw(create_result.stdout)
    assert created_redirect

    update_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "update-by-id",
            str(created_redirect.id),
            "--url",
            str(new_url),
            "--short-link",
            str(new_short_link),
            "--response-status",
            str(new_response_status),
            "--body",
            str(new_body),
        ],
    )

    assert update_result.exit_code == 0, f"search result: {update_result}"
    updated_redirect = Redirect.parse_raw(update_result.stdout)
    assert updated_redirect
    assert updated_redirect.url == new_url
    assert updated_redirect.short_link == new_short_link
    assert updated_redirect.response_status == new_response_status
    assert updated_redirect.body == new_body


async def test_update_body(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "if only the body is modified, does all other info stay the same?"
    url = unsafe_random_string(test_string_length)
    short_link = random_short_link(test_string_length)
    response_status = int(test_string_length)

    body = unsafe_random_string(test_string_length)
    new_body = unsafe_random_string(test_string_length)
    assert new_body != body

    create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link),
            "--response-status",
            str(response_status),
            "--body",
            str(body),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_redirect = Redirect.parse_raw(create_result.stdout)
    assert created_redirect

    update_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "update-by-id",
            str(created_redirect.id),
            "--body",
            str(new_body),
        ],
    )

    assert update_result.exit_code == 0, f"search result: {update_result}"
    updated_redirect = Redirect.parse_raw(update_result.stdout)
    assert updated_redirect
    assert updated_redirect.url == url
    assert updated_redirect.short_link == short_link
    assert updated_redirect.response_status == response_status
    assert updated_redirect.body == new_body


async def test_update_none(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "if nothing is updated, will the same info be returned?"
    url = unsafe_random_string(test_string_length)
    short_link = random_short_link(test_string_length)
    response_status = int(test_string_length)
    body = unsafe_random_string(test_string_length)

    create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            str(short_link),
            "--response-status",
            str(response_status),
            "--body",
            str(body),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_redirect = Redirect.parse_raw(create_result.stdout)
    assert created_redirect

    update_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "update-by-id",
            str(created_redirect.id),
        ],
    )

    assert update_result.exit_code == 0, f"search result: {update_result}"
    updated_redirect = Redirect.parse_raw(update_result.stdout)
    assert updated_redirect
    assert updated_redirect == created_redirect


async def test_redirect_create_empty_short_link(
    on_disk_database: Path,
    run_test_command: CommandRunner,
    test_string_length: int,
) -> None:
    "if the short link is unspecified, will a random one be chosen?"
    url = unsafe_random_string(test_string_length)
    response_status = int(test_string_length)
    body = unsafe_random_string(test_string_length)

    create_result = await run_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "local",
            "--database-path",
            str(on_disk_database),
            "redirect",
            "create",
            str(url),
            "--response-status",
            str(response_status),
            "--body",
            str(body),
        ],
    )

    assert create_result.exit_code == 0, f"result: {create_result}"
    created_redirect = Redirect.parse_raw(create_result.stdout)
    assert created_redirect
    assert created_redirect.url == url
    assert hasattr(created_redirect, "short_link")
    assert len(created_redirect.short_link) == defaults.short_link_length
    # is the short link only made up of characters from the default character
    # set?
    assert set(created_redirect.short_link) <= set(defaults.short_link_characters)
    assert created_redirect.response_status == response_status
    assert created_redirect.body == body
