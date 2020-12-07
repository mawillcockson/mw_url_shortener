print(f"imported mw_url_shortener.database.interface as {__name__}")
from pony.orm import db_session, Database
from . import db
from .entities import RedirectEntity, UserEntity
from .models import Redirect, User
from pathlib import Path
from typing import Union, Optional
from .. import Key, Uri, Username, HashedPassword
from sqlite3 import DatabaseError
from pony.orm.dbapiprovider import DBException


SPath = Union[str, Path]


def valid_database_file(filename: SPath) -> bool:
    "Opens a connection to a database file, and runs a quick database check"
    path = Path(filename).resolve()
    if not path.is_file():
        return False

    temp_db = Database()
    try:
        temp_db.bind(provider="sqlite", filename=str(path), create_db=False)
        # From:
        # https://stackoverflow.com/a/21146372
        schema_version = temp_db.execute("pragma schema_version;").fetchone()[0]
        quick_check = temp_db.execute("pragma quick_check;").fetchone()[0]
    # NOTE:FEATURE::DATABASE update with exceptions from other database drivers
    except (DatabaseError, DBException) as err:
        return False
    finally:
        temp_db.disconnect()

    if quick_check != "ok":
        return False

    return True


def create_database_file(filename: SPath) -> None:
    "Creates a database file if it doesn't exist"
    path = Path(filename).resolve()
    if path.exists():
        raise FileExistsError(f"'{path}' already exists")

    try:
        path.touch()
    except OSError as err:
        raise ValueError(f"cannot create database file at '{path}'") from err


# NOTE: I really don't like this interface
# Should the Database() object be created outside thie module and passed
# into this function?
# If so, how would the entities in entities.py be declared without a
# Database() object?
# NOTE:FEATURE::DATABASE Currently, only a SQLite database is supported
def set_database_file_and_connect(filename: SPath) -> Database:
    """
    Connects pony's database engine to a physical file on disk
    """
    path = Path(filename).resolve()
    if not path.exists():
        create_database_file(filename=path)
    elif path.exists() and not path.is_file():
        raise ValueError(f"expected database file, '{path}' is not a file")

    if not valid_database_file(filename=path):
        raise ValueError(f"'{path}' is not a valid database file")

    db.bind(provider="sqlite", filename=str(path), create_db=False)
    return db


def generate_mapping(create_tables: bool = True) -> Database:
    """
    Maps the declared entities to tables in the database, creating them if necessary

    Should be called after the entities have been added to the database object
    """
    db.generate_mapping(create_tables=create_tables)
    return db


def get_redirect(key: Key) -> Redirect:
    missing_redirect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No redirect found",
    )

    with db_session:
        redirect = RedirectInDB.get(key=key)
        if redirect is None:
            raise missing_redirect

        return Redirect.from_orm(redirect)


def add_redirect(redirect: Redirect) -> Redirect:
    "add a Redirect to the database, and verify that it's represented correctly"
    with db_session:
        new_redirect = Redirect.from_orm(RedirectEntity(key=redirect.key, url=redirect.url))
    assert redirect == new_redirect, "Database mutated data"
    return new_redirect


def get_user(username: str) -> Optional[User]:
    "Looks up user in the database, and builds a User model"
    with db_session:
        user = UserInDB.get(username=username)
        if not user:
            return None

    return User(username=user.username, hashed_password=user.hashed_password)
