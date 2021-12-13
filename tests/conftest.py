import sqlite3
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener.database.start import make_session


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
    _ = await make_session("sqlite+aiosqlite:///" + str(tmp_db))
    return tmp_db


@pytest.fixture
async def in_memory_database(anyio_backend: str) -> AsyncSession:
    return await make_session("sqlite+aiosqlite:///:memory:")
