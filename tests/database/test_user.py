"""
does the database interface behave as expected?
"""
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener import database_interface
from mw_url_shortener.security import verify_password
from mw_url_shortener.schemas.user import UserCreate, UserUpdate

from tests.utils import random_password, random_username


async def test_create_user(in_memory_database: AsyncSession) -> None:
    "can a user be added to the database?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user = await database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema
    )
    assert user.username == username
    assert hasattr(user, "hashed_password")


async def test_authenticate_user(in_memory_database: AsyncSession) -> None:
    "can an added user's data be used to authenticate the user?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema
    )
    user_authenticated = database_interface.user.authenticate(
        in_memory_database, username=username, password=password
    )
    assert user_authenticated
    assert user_created.email == user_authenticated.email


async def test_not_authenticate_user(in_memory_database: AsyncSession) -> None:
    "will authentication fail for user data not in the database?"
    username = random_username()
    password = random_password()
    user_created = await database_interface.user.authenticate(
        db, username=username, password=password
    )
    assert user_created is None


async def test_get_user(in_memory_database: AsyncSession) -> None:
    "can a previously added user be retrieved by id, and is the data the same?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = await database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema
    )
    user_retrieved = await database_interface.user.get_by_id(in_memory_database, id=user.id)
    assert user_retrieved
    assert user_created.email == user_retrieved.email
    assert jsonable_encoder(user_created) == jsonable_encoder(user_retrieved)


async def test_update_user(in_memory_database: AsyncSession) -> None:
    "if a user is modified, does the database return the modified user?"
    username = random_username()
    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    user_created = database_interface.user.create(
        in_memory_database, object_schema_in=user_create_schema
    )
    new_password = random_password()
    user_update_schema = UserUpdate(password=new_password)
    database_interface.user.update(
        in_memory_database, current_in_db=user, update_schema=user_in_update
    )
    user_retrieved = database_interface.user.get_by_id(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)
