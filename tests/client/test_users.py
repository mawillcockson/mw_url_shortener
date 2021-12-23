"""
do all cli commands dealing with users work correctly?
"""
from pathlib import Path

from sqlalchemy import and_, select
from typer.testing import CliRunner

from mw_url_shortener.cli.entry_point import app

from .utils import random_password, random_username

runner = CliRunner()

# NOTE:BUG isort can't handle the below syntax

# def test_create_user(on_disk_database: Path) -> None:
#     "can a user be created and read back?"
#     test_username = random_username()
#     test_password = random_password()
#
#     result = runner.invoke(
#         app,
#         [
#             "--local",
#             str(on_disk_database),
#             "user",
#             "create",
#             "--username",
#             test_username,
#             "--password",
#             test_password,
#         ],
#     )
#     assert result.exit_code == 0
#     assert (
#         f"user '{test_username}' created with id '{expected_user_id}'" in result.stdout
#     )
#
#     retrieved_user = await database_interface.user.get_by_id()
