"""
does the database interface behave as expected?
"""
import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener import database_interface
from mw_url_shortener.schemas.user import UserCreate, UserUpdate
from mw_url_shortener.security import verify_password
from tests.utils import random_password, random_username


async def test_get_nonexistent_user_by_id(in_memory_database: AsyncSession) -> None:
    "does get_by_id() fail if the database is empty?"
    with pytest.raises(NoResultFound):
        assert not database_interface.user.get_by_id(in_memory_database, id=0)

    with pytest.raises(NoResultFound):
        assert not database_interface.user.get_by_id(in_memory_database, id=1)


async def test_create_user(in_memory_database: AsyncSession) -> None:
    "can a user be added to the database?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user = await database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema
    )
    assert user.username == username
    assert hasattr(user, "id")


async def test_authenticate_user(in_memory_database: AsyncSession) -> None:
    "can an added user's data be used to authenticate the user?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema
    )
    user_authenticated = await database_interface.user.authenticate(
        in_memory_database, username=username, password=password
    )
    assert user_authenticated
    assert user_created.username == user_authenticated.username


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
        in_memory_database, object_schema_in=user_create_schema
    )
    user_retrieved = await database_interface.user.get_by_id(
        in_memory_database, id=user_created.id
    )
    assert user_retrieved
    assert user_created.username == user_retrieved.username
    assert jsonable_encoder(user_created) == jsonable_encoder(user_retrieved)


async def test_get_two_users(in_memory_database: AsyncSession) -> None:
    "can a previous two users be retrieved simultaneously?"
    username1 = random_username()
    password1 = random_password()
    user_create_schema1 = UserCreate(username=username1, password=password1)
    user_created1 = await database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema1
    )

    username2 = random_username()
    password2 = random_password()
    user_create_schema2 = UserCreate(username=username2, password=password2)
    user_created2 = await database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema2
    )

    retrieved_users = await database_interface.user.get_multiple(
        in_memory_database, skip=0, limit=100
    )
    assert len(retrieved_users) == 2
    retrieved_user_data = list(map(jsonable_encoder, retrieved_users))
    user1_data = jsonable_encoder(user_created1)
    user2_data = jsonable_encoder(user_created2)
    assert user1_data in retrieved_user_data
    assert user2_data in retrieved_user_data


async def test_update_user(in_memory_database: AsyncSession) -> None:
    "if a user is modified, does the database return the modified user?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema
    )
    new_password = random_password()
    user_update_schema = UserUpdate(password=new_password)
    await database_interface.user.update(
        in_memory_database,
        current_object_schema=user_created,
        object_update_schema=user_update_schema,
    )
    user_retrieved = await database_interface.user.get_by_id(
        in_memory_database, id=user_created.id
    )
    assert user_retrieved
    assert user_created.username == user_retrieved.username
    authenticated_user = await database_interface.user.authenticate(
        in_memory_database, username=user_retrieved.username, password=new_password
    )
    assert authenticated_user


async def test_delete_user(in_memory_database: AsyncSession) -> None:
    "if a user is deleted, can their data no longer be found in the database?"
    # create user
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database,
        object_schema_in=user_create_schema,
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
    with pytest.raises(NoResultFound):
        await database_interface.user.get_by_id(
            in_memory_database, id=user_retrieved.id
        )
