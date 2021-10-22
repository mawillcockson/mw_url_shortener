"""
do all cli commands dealing with users work correctly?
"""
from pathlib import Path

from typer.testing import CliRunner

from mw_url_shortener.client.cli import app
from sqlalchemy import and_, select
from mw_url_shortener.security import hash_password

runner = CliRunner()


def test_create_user(on_disk_database: Path) -> None:
    "can a user be created and read back?"
    test_username = "test"
    test_password = "password"
    expected_user_id = 0

    result = runner.invoke(
        app,
        [
            "--local",
            str(on_disk_database),
            "user",
            "create",
            "--username",
            test_username,
            "--password",
            test_password,
        ],
    )
    assert result.exit_code == 0
    assert f"user '{test_username}' created with id '{expected_user_id}'" in result.stdout
    user_in_db = (
        select(UserInDB)
        .where(and_(UserInDB.username == test_username, UserInDB.id == test_user_id))
        .one()
    )
    assert user_in_db.username == test_username
    assert user_in_db.hashed_password == hash_password(test_password)
