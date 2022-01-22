"""
can the app take all of it's configuration through command line parameters?
"""
from pathlib import Path
from pprint import pformat

import inject

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.dependency_injection.settings import get_settings
from mw_url_shortener.schemas.redirect import random_short_link
from mw_url_shortener.settings import FlexibleSettings, OutputStyle, Settings, defaults
from tests.utils import random_password, random_username

from .conftest import CommandRunner


async def test_main(run_basic_test_command: CommandRunner) -> None:
    "can show-configuration be called from the main command group?"
    result = await run_basic_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "show-configuration",
        ],
    )

    assert result.exit_code == 0, f"result: {result}"
    assert result.stdout
    returned_settings = FlexibleSettings.parse_raw(result.stdout)

    # affirm that there's no difference between unconfigured settings and what
    # was returned
    settings = Settings(output_style=OutputStyle.json)
    settings_data = settings.dict()
    updated_settings = returned_settings.copy(update=settings_data)
    differences = pformat(
        {
            key: {
                "returned_settings": value,
                "updated_settings": getattr(updated_settings, key),
            }
            for key, value in returned_settings
            if not hasattr(updated_settings, key)
            or getattr(updated_settings, key) != value
        },
        indent=2,
    )
    assert updated_settings == returned_settings, f"{differences}"


async def test_local(
    tmp_path: Path,
    run_basic_test_command: CommandRunner,
) -> None:
    "is the database path accepted as a command-line parameter?"
    database_path = tmp_path / "temporary_database.sqlite"

    result = await run_basic_test_command(
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

    returned_settings = FlexibleSettings.parse_raw(result.stdout)
    assert returned_settings.database_path == database_path

    # make sure no local files were modified
    assert not database_path.exists()


async def test_remote(run_basic_test_command: CommandRunner) -> None:
    """
    are the base_url, username, and password accepted as command line
    parameters?
    """
    base_url = "http://does-not-matter"
    api_prefix = random_short_link(10)
    username = random_username()
    password = random_password()

    result = await run_basic_test_command(
        app,
        [
            "--output-style",
            OutputStyle.json.value,
            "remote",
            "--base-url",
            base_url,
            "--api-prefix",
            api_prefix,
            "--username",
            username,
            "--password",
            password,
            "show-configuration",
        ],
        clear_injection=False,
    )

    assert result.exit_code == 0, f"result: {result}"

    returned_settings = FlexibleSettings.parse_raw(result.stdout)
    assert returned_settings.base_url == base_url
    assert returned_settings.api_base_url == base_url + "/" + api_prefix + "/"
    assert returned_settings.username == username  # type: ignore
    assert returned_settings.password == password  # type: ignore

    settings = get_settings()
    assert not hasattr(settings, "password"), f"could risk storing password"

    inject.clear()
