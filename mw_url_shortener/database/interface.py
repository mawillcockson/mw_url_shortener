print(f"imported mw_url_shortener.database.interface as {__name__}")
from pathlib import Path
from sqlite3 import DatabaseError
from typing import List, Optional, Union

from fastapi import Depends
from pony.orm import Database, db_session
from pony.orm.dbapiprovider import DBException

from ..types import HashedPassword, Key, SPath, Uri, Username
from . import get_db
from .errors import DatabaseError, UserAlreadyExistsError, UserNotFoundError
from .models import RedirectModel, UserModel


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
        with db_session:
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
def set_database_file_and_connect(db: Database, filename: SPath) -> Database:
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


def generate_mapping(db: Database, create_tables: bool = True) -> Database:
    """
    Maps the declared entities to tables in the database, creating them if necessary

    Should be called after the entities have been added to the database object
    """
    db.generate_mapping(create_tables=create_tables)
    return db


def setup_db(db: Database, filename: SPath, create_tables: bool = True) -> Database:
    """
    convencience function combining set_database_file_and_connect and
    generate_mapping
    """
    set_database_file_and_connect(db=db, filename=filename)
    return generate_mapping(db=db, create_tables=create_tables)


def get_redirect(key: Key, db: Database = Depends(get_db)) -> RedirectModel:
    with db_session:
        redirect = db.RedirectEntity.get(key=key)
        if not redirect:
            raise KeyError("redirect key not found")

        return RedirectModel.from_orm(redirect)


def create_redirect(
    redirect: RedirectModel, db: Database = Depends(get_db)
) -> RedirectModel:
    "add a redirect to the database, and verify that it's represented correctly"
    with db_session:
        new_redirect = RedirectModel.from_orm(
            db.RedirectEntity(key=redirect.key, uri=redirect.uri)
        )
    assert redirect == new_redirect, "Database mutated data"
    return new_redirect


def update_redirect():
    raise NotImplementedError


def delete_redirect():
    raise NotImplementedError


def get_redirect():
    raise NotImplementedError


def list_redirects():
    raise NotImplementedError


def new_redirect_key():
    raise NotImplementedError


def get_user(username: Username, db: Database = Depends(get_db)) -> UserModel:
    "Looks up user in the database, and builds a User model"
    with db_session:
        user = db.UserEntity.get(username=username)
        if not user:
            raise UserNotFoundError(f"no user found with username '{username}'")

        return UserModel.from_orm(user)


def create_user(user: UserModel, db: Database = Depends(get_db)) -> UserModel:
    "adds a user to the database"
    try:
        get_user(db=db, username=user.username)
    except UserNotFoundError as err:
        pass
    else:
        raise UserAlreadyExistsError(
            f"a user with username '{user.username}' already exists"
        )
    with db_session:
        return UserModel.from_orm(
            db.UserEntity(username=user.username, hashed_password=user.hashed_password)
        )


def list_users(db: Database = Depends(get_db)) -> List[UserModel]:
    """
    returns a list of all the current users in the database

    the list may be empty
    """
    with db_session:
        return list(UserModel.from_orm(user) for user in db.UserEntity.select())


def delete_user(user: UserModel, db: Database = Depends(get_db)) -> None:
    "deletes a user"
    with db_session:
        user_entity = db.UserEntity.get(username=user.username)
        if not user_entity:
            raise UserNotFoundError(f"no user found with username '{user.username}'")

        user_entity.delete()


def update_user(
    username: Username, updated_user: UserModel, db: Database = Depends(get_db)
) -> UserModel:
    "updates a user in the database using the new user data"
    with db_session:
        old_user_entity = db.UserEntity.get(username=updated_user.username)

        if not old_user_entity:
            raise UserNotFoundError(f"no user found with username '{username}'")

        if old_user_entity.username != updated_user.username:
            create_user(db=db, user=updated_user)
            old_user_entity.delete()
        else:
            old_user_entity.hashed_password = updated_user.hashed_password

        return UserModel.from_orm(db.UserEntity.get(username=updated_user.username))
