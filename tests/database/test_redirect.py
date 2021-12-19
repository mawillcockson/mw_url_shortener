# mypy: allow_any_expr
"""
does the database interface behave as expected?
"""
from re import escape

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener import database_interface
from mw_url_shortener.schemas.redirect import (
    RedirectCreate,
    RedirectUpdate,
    random_short_link,
)
from mw_url_shortener.settings import defaults
from mw_url_shortener.utils import unsafe_random_string


async def test_create_redirect_defaults(in_memory_database: AsyncSession) -> None:
    "if no values are provides, is a redirected created with default values?"
    create_redirect_schema = RedirectCreate()

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )
    assert created_redirect
    assert hasattr(created_redirect, "id")

    assert hasattr(created_redirect, "short_link")
    assert len(created_redirect.short_link) == defaults.short_link_length
    short_link_characters = set(created_redirect.short_link)
    allowed_characters = set(defaults.short_link_characters)
    assert short_link_characters.issubset(allowed_characters)

    assert hasattr(created_redirect, "url")
    assert created_redirect.url == defaults.redirect_url

    assert hasattr(created_redirect, "response_status")
    assert created_redirect.response_status == defaults.redirect_response_status

    assert hasattr(created_redirect, "body")
    assert created_redirect.body == defaults.redirect_body


async def test_create_redirect(in_memory_database: AsyncSession) -> None:
    "will the redirect have the custom properties set if they're provided?"
    short_link = random_short_link(defaults.test_string_length)
    assert len(short_link) == defaults.test_string_length

    url = unsafe_random_string(defaults.test_string_length)
    assert len(url) == defaults.test_string_length

    response_status = int(defaults.test_string_length)

    body = unsafe_random_string(defaults.test_string_length)
    # already made sure unsafe_random_string() is making strings of the correct
    # length

    create_redirect_schema = RedirectCreate(
        short_link=short_link, url=url, response_status=response_status, body=body
    )

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )
    assert created_redirect

    assert created_redirect.short_link == short_link
    assert created_redirect.url == url
    assert created_redirect.response_status == response_status
    assert created_redirect.body == body


async def test_create_non_unique_short_link(in_memory_database: AsyncSession) -> None:
    """
    will the database reject a redirect that has the same short link as another
    redirect?
    """
    short_link = random_short_link()
    create_redirect_schema = RedirectCreate(short_link=short_link)
    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )

    with pytest.raises(IntegrityError) as error:
        created_redirect2 = await database_interface.redirect.create(
            in_memory_database, create_object_schema=create_redirect_schema
        )
    assert error.match(escape("UNIQUE constraint failed"))


async def test_create_unique_short_link(in_memory_database: AsyncSession) -> None:
    "will the database accept two redirects with only a short link different?"
    short_link = random_short_link(defaults.test_string_length)
    assert len(short_link) == defaults.test_string_length

    url = unsafe_random_string(defaults.test_string_length)
    assert len(url) == defaults.test_string_length

    response_status = int(defaults.test_string_length)

    body = unsafe_random_string(defaults.test_string_length)
    # already made sure unsafe_random_string() is making strings of the correct
    # length

    first_redirect_schema = RedirectCreate(
        short_link=short_link, url=url, response_status=response_status, body=body
    )

    first_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=first_redirect_schema
    )

    new_short_link = random_short_link(defaults.test_string_length)
    second_redirect_schema = first_redirect_schema.copy(
        update={"short_link": new_short_link}
    )

    second_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=second_redirect_schema
    )
    assert second_redirect

    assert second_redirect.short_link != first_redirect.short_link
    exclude_attributes = {"id", "short_link"}
    first_redirect_data_no_short_link = first_redirect.dict(exclude=exclude_attributes)
    second_redirect_data_no_short_link = second_redirect.dict(
        exclude=exclude_attributes
    )
    assert first_redirect_data_no_short_link == second_redirect_data_no_short_link


async def redirect_get_by_id(in_memory_database: AsyncSession) -> None:
    create_redirect_schema = RedirectCreate()

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )

    retrieved_redirect = await database_interface.redirect.get_by_id(
        in_memory_database, id=created_redirect.id
    )

    assert retrieved_redirect == created_redirect


async def test_redirect_get_by_short_link(in_memory_database: AsyncSession) -> None:
    short_link = random_short_link(defaults.test_string_length)
    create_redirect_schema = RedirectCreate(short_link=short_link)

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )

    retrieved_redirect = await database_interface.redirect.get_by_short_link(
        in_memory_database, short_link=created_redirect.short_link
    )

    assert retrieved_redirect == created_redirect


async def test_redirect_get_by_url(in_memory_database: AsyncSession) -> None:
    url = unsafe_random_string(defaults.test_string_length)
    create_redirect_schema = RedirectCreate(url=url)

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )

    retrieved_redirects = await database_interface.redirect.get_by_url(
        in_memory_database, url=created_redirect.url
    )

    assert len(retrieved_redirects) == 1
    assert created_redirect in retrieved_redirects


async def test_redirect_get_by_response_status(
    in_memory_database: AsyncSession,
) -> None:
    response_status = int(defaults.test_string_length)
    create_redirect_schema = RedirectCreate(response_status=response_status)

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )

    retrieved_redirects = await database_interface.redirect.get_by_response_status(
        in_memory_database, response_status=created_redirect.response_status
    )

    assert len(retrieved_redirects) == 1
    assert created_redirect in retrieved_redirects


async def test_redirect_get_by_body(in_memory_database: AsyncSession) -> None:
    body = unsafe_random_string(defaults.test_string_length)
    create_redirect_schema = RedirectCreate(body=body)

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )

    retrieved_redirects = await database_interface.redirect.get_by_body(
        in_memory_database, body=created_redirect.body
    )

    assert len(retrieved_redirects) == 1
    assert created_redirect in retrieved_redirects


# redirect_get_two
# redirect_update_short_link
# redirect_update_url
# redirect_update_response_status
# redirect_update_body
# redirect_remove_by_id


# async def test_get_user_by_id(in_memory_database: AsyncSession) -> None:
#     "can a previously added user be retrieved by id, and is the data the same?"
#     username = random_username()
#     password = random_password()
#     user_create_schema = UserCreate(username=username, password=password)
#     user_created = await database_interface.user.create(
#         in_memory_database, create_object_schema=user_create_schema
#     )
#     user_retrieved = await database_interface.user.get_by_id(
#         in_memory_database, id=user_created.id
#     )
#     assert user_retrieved
#     assert user_created == user_retrieved
#
#
# async def test_get_two_users(in_memory_database: AsyncSession) -> None:
#     "can a previous two users be retrieved simultaneously?"
#     username1 = random_username()
#     password1 = random_password()
#     user_create_schema1 = UserCreate(username=username1, password=password1)
#     user_created1 = await database_interface.user.create(
#         in_memory_database, create_object_schema=user_create_schema1
#     )
#
#     username2 = random_username()
#     password2 = random_password()
#     user_create_schema2 = UserCreate(username=username2, password=password2)
#     user_created2 = await database_interface.user.create(
#         in_memory_database, create_object_schema=user_create_schema2
#     )
#
#     retrieved_users = await database_interface.user.get_multiple(
#         in_memory_database, skip=0, limit=100
#     )
#     assert len(retrieved_users) == 2
#     assert user_created1 in retrieved_users
#     assert user_created2 in retrieved_users
#
#
# async def test_update_user_password(in_memory_database: AsyncSession) -> None:
#     """
#     if a user password is modified, does the database return the modified user?
#     """
#     username = random_username()
#     password = random_password()
#     user_create_schema = UserCreate(username=username, password=password)
#     user_created = await database_interface.user.create(
#         in_memory_database, create_object_schema=user_create_schema
#     )
#
#     new_password = random_password()
#     user_update_schema = UserUpdate(password=new_password)
#
#     await database_interface.user.update(
#         in_memory_database,
#         current_object_schema=user_created,
#         update_object_schema=user_update_schema,
#     )
#
#     user_retrieved = await database_interface.user.get_by_id(
#         in_memory_database, id=user_created.id
#     )
#
#     assert user_retrieved
#     assert user_created == user_retrieved
#
#     # affirm authentication fails if the old password is used
#     authentication_with_old_password = await database_interface.user.authenticate(
#         in_memory_database, username=user_retrieved.username, password=password
#     )
#     assert not authentication_with_old_password
#
#     # affirm authentication succeeds when new password is used
#     authenticated_user = await database_interface.user.authenticate(
#         in_memory_database, username=user_retrieved.username, password=new_password
#     )
#     assert authenticated_user
#     assert authenticated_user == user_created
#
#
# async def test_delete_user(in_memory_database: AsyncSession) -> None:
#     "if a user is deleted, can their data no longer be found in the database?"
#     # create user
#     username = random_username()
#     password = random_password()
#     user_create_schema = UserCreate(username=username, password=password)
#     user_created = await database_interface.user.create(
#         in_memory_database,
#         create_object_schema=user_create_schema,
#     )
#
#     # affirm user is in database
#     user_retrieved = await database_interface.user.get_by_id(
#         in_memory_database, user_created.id
#     )
#     # roundtripping with get_by_id() is tested more thoroughly elsewhere, no
#     # need to test it again here
#     assert user_retrieved
#
#     deleted_user = await database_interface.user.remove_by_id(
#         in_memory_database, id=user_retrieved.id
#     )
#     assert deleted_user == user_created
#     with pytest.raises(NoResultFound):
#         await database_interface.user.get_by_id(
#             in_memory_database, id=user_retrieved.id
#         )
