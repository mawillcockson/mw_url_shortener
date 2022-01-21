"""
these tests ensure old buggy behaviour hasn't been reintroduced
"""
from mw_url_shortener.cli.entry_point import app
from tests.cli.conftest import CommandRunner
from tests.utils import random_password


async def test_encoding(run_test_command: CommandRunner) -> None:
    """
    if a response indicates the content media type is application/json, does
    not indicate a charset, and contains a string that looks like it's a
    non-UTF-8 byte sequence, will the client still correctly use utf-8?
    """
    problem_username = "i\n3?\"Ru7/v\x0c\r'M|I$H<HiMiEyd[I)"
    password = random_password()

    result = await run_test_command(
        app,
        [
            "user",
            "create",
            "--username",
            problem_username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0, f"regression\nresult: {result}"
