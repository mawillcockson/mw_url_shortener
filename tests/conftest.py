import sqlite3
from pathlib import Path
from typing import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener.database.start import make_sessionmaker


@pytest.fixture(scope="session")
def test_string_length() -> int:
    "the length of most dynamic strings in the test suite"
    # use a ridiculous number so things break earlier
    # not too ridiculous so the tests don't take too long
    return 100_000


@pytest.fixture
def anyio_backend() -> str:
    "declares the backend to use for all async tests"
    # SQLAlchemy uses a sqlite DBAPI (aiosqlite) that depends upon asyncio
    return "asyncio"


@pytest.fixture
def empty_on_disk_database(tmp_path: Path) -> Path:
    tmp_db = tmp_path / "on_disk_database"

    # Taken from:
    # https://github.com/kvesteri/sqlalchemy-utils/blob/b262d2d33a2ff6cb3b3dbabb25680d4686c7c18a/sqlalchemy_utils/functions/database.py#L591-L593
    with sqlite3.connect(str(tmp_db)) as connection:
        connection.execute("CREATE TABLE DB(id int);")
        connection.execute("DROP TABLE DB;")

    print(tmp_db)
    return tmp_db


@pytest.fixture
async def on_disk_database(tmp_path: Path, anyio_backend: str) -> Path:
    tmp_db = tmp_path / "on_disk_database"
    _ = await make_sessionmaker("sqlite+aiosqlite:///" + str(tmp_db))
    return tmp_db


@pytest.fixture
async def in_memory_database(anyio_backend: str) -> AsyncIterator[AsyncSession]:
    async_sessionmaker = await make_sessionmaker("sqlite+aiosqlite:///:memory:")
    async with async_sessionmaker() as async_session:
        yield async_session
