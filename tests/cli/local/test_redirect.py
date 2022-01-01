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
) -> None:
    "can a redirect be created and read back?"
    url = defaults.redirect_url
    short_link = random_short_link(defaults.test_string_length)

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
) -> None:
    "can a redirect be created and read back?"
    url = unsafe_random_string(defaults.test_string_length)
    short_link = random_short_link(defaults.test_string_length)
    response_status = int(defaults.test_string_length)
    body = unsafe_random_string(defaults.test_string_length)

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
) -> None:
    "can a redirect be retrieved by id?"
    url = unsafe_random_string(defaults.test_string_length)
    short_link = random_short_link(defaults.test_string_length)
    response_status = int(defaults.test_string_length)
    body = unsafe_random_string(defaults.test_string_length)

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


async def test_get_non_existant_redirect(
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
