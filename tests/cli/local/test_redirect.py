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