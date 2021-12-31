"""
does the database interface behave as expected?
"""
from typing import List

import pytest

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
from mw_url_shortener.security import verify_password
from tests.utils import random_password, random_username


async def test_get_nonexistent_user_by_id(in_memory_database: AsyncSession) -> None:
    "does get_by_id() fail if the database is empty?"
    non_existant_user = await database_interface.user.get_by_id(
        in_memory_database, id=0
    )
    assert not non_existant_user

    non_existant_user = await database_interface.user.get_by_id(
        in_memory_database, id=1
    )
    assert not non_existant_user


async def test_create_user(in_memory_database: AsyncSession) -> None:
    "can a user be added to the database?"
    username = random_username()
    password = random_password()
    create_user_schema = UserCreate(username=username, password=password)
    created_user = await database_interface.user.create(
        in_memory_database, create_object_schema=create_user_schema
    )
    assert created_user.username == username
    assert hasattr(created_user, "id")
    assert created_user.id is not None
    assert not hasattr(created_user, "hashed_password")


async def test_authenticate_user(in_memory_database: AsyncSession) -> None:
    "can an added user's data be used to authenticate the user?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database, create_object_schema=user_create_schema
    )
    user_authenticated = await database_interface.user.authenticate(
        in_memory_database, username=username, password=password
    )
    assert user_authenticated
    assert user_authenticated == user_created


async def test_not_authenticate_user(in_memory_database: AsyncSession) -> None:
    "will authentication fail for user data not in the database?"
    username = random_username()
    password = random_password()
    user_created = await database_interface.user.authenticate(
        in_memory_database, username=username, password=password
    )
    assert user_created is None


async def test_get_user_by_id(in_memory_database: AsyncSession) -> None:
    "can a previously added user be retrieved by id, and is the data the same?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database, create_object_schema=user_create_schema
    )
    user_retrieved = await database_interface.user.get_by_id(
        in_memory_database, id=user_created.id
    )
    assert user_retrieved
    assert user_created == user_retrieved


async def test_get_user_by_username(in_memory_database: AsyncSession) -> None:
    """
    can a previously added user be retrieved by username, and is the data the
    same?
    """
    username1 = random_username()
    password1 = random_password()
    user_create_schema1 = UserCreate(username=username1, password=password1)
    user_created1 = await database_interface.user.create(
        in_memory_database, create_object_schema=user_create_schema1
    )

    username2 = random_username()
    password2 = random_password()
    user_create_schema2 = UserCreate(username=username2, password=password2)
    user_created2 = await database_interface.user.create(
        in_memory_database, create_object_schema=user_create_schema2
    )

    retrieved_user1 = await database_interface.user.get_by_username(
        in_memory_database, username=username1
    )
    assert retrieved_user1
    assert retrieved_user1 == user_created1


async def test_get_two_users(in_memory_database: AsyncSession) -> None:
    "can a previous two users be retrieved simultaneously?"
    username1 = random_username()
    password1 = random_password()
    user_create_schema1 = UserCreate(username=username1, password=password1)
    user_created1 = await database_interface.user.create(
        in_memory_database, create_object_schema=user_create_schema1
    )

    username2 = random_username()
    password2 = random_password()
    user_create_schema2 = UserCreate(username=username2, password=password2)
    user_created2 = await database_interface.user.create(
        in_memory_database, create_object_schema=user_create_schema2
    )

    retrieved_users = await database_interface.user.get_multiple(
        in_memory_database, skip=0, limit=100
    )
    assert len(retrieved_users) == 2
    assert user_created1 in retrieved_users
    assert user_created2 in retrieved_users


async def test_update_user_password(in_memory_database: AsyncSession) -> None:
    """
    if a user password is modified, does the database return the modified user?
    """
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database, create_object_schema=user_create_schema
    )

    new_password = random_password()
    user_update_schema = UserUpdate(password=new_password)

    await database_interface.user.update(
        in_memory_database,
        current_object_schema=user_created,
        update_object_schema=user_update_schema,
    )

    user_retrieved = await database_interface.user.get_by_id(
        in_memory_database, id=user_created.id
    )

    assert user_retrieved
    assert user_created == user_retrieved

    # affirm authentication fails if the old password is used
    authentication_with_old_password = await database_interface.user.authenticate(
        in_memory_database, username=user_retrieved.username, password=password
    )
    assert not authentication_with_old_password

    # affirm authentication succeeds when new password is used
    authenticated_user = await database_interface.user.authenticate(
        in_memory_database, username=user_retrieved.username, password=new_password
    )
    assert authenticated_user
    assert authenticated_user == user_created


async def test_delete_user_by_id(in_memory_database: AsyncSession) -> None:
    "if a user is deleted, can their data no longer be found in the database?"
    # create user
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database,
        create_object_schema=user_create_schema,
    )

    # affirm user is in database
    user_retrieved = await database_interface.user.get_by_id(
        in_memory_database, user_created.id
    )
    # roundtripping with get_by_id() is tested more thoroughly elsewhere, no
    # need to test it again here
    assert user_retrieved

    deleted_user = await database_interface.user.remove_by_id(
        in_memory_database, id=user_retrieved.id
    )
    assert deleted_user == user_created

    non_existant_user = await database_interface.user.get_by_id(
        in_memory_database, id=user_retrieved.id
    )
    assert not non_existant_user


async def test_search_by_everything(in_memory_database: AsyncSession) -> None:
    """
    if a few similar users are in the database, can a specific one be
    retrieved?
    """
    username = random_username()
    other_username1 = random_username()
    other_username2 = random_username()
    # affirm all are unique
    assert len({username, other_username1, other_username2}) == 3

    password = random_password()
    other_password = random_password()
    assert password != other_password

    desired_user_schema = UserCreate(username=username, password=password)

    desired_user = await database_interface.user.create(
        in_memory_database, create_object_schema=desired_user_schema
    )
    assert desired_user

    other_user_schema1 = UserCreate(username=other_username1, password=password)
    other_user_schema2 = UserCreate(username=other_username2, password=other_password)

    other_users: List[User] = []
    for other_user_schema in [other_user_schema1, other_user_schema2]:
        other_user = await database_interface.user.create(
            in_memory_database, create_object_schema=other_user_schema
        )
        assert other_user
        other_users.append(other_user)

    assert desired_user not in other_users

    retrieved_users = await database_interface.user.search(
        in_memory_database, username=username
    )
    assert len(retrieved_users) == 1, str(retrieved_users)
    assert desired_user in retrieved_users
