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


async def test_get_two_redirects(in_memory_database: AsyncSession) -> None:
    "can a previous two redirects be retrieved simultaneously?"
    first_short_link = random_short_link(defaults.test_string_length)
    second_short_link = random_short_link(defaults.test_string_length)

    first_redirect_schema = RedirectCreate(short_link=first_short_link)
    second_redirect_schema = RedirectCreate(short_link=second_short_link)

    first_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=first_redirect_schema
    )
    second_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=second_redirect_schema
    )

    assert first_redirect != second_redirect

    retrieved_multiple = await database_interface.redirect.get_multiple(
        in_memory_database, skip=0, limit=100
    )

    assert len(retrieved_multiple) == 2
    assert first_redirect in retrieved_multiple
    assert second_redirect in retrieved_multiple


async def test_update_redirect(in_memory_database: AsyncSession) -> None:
    "if all attributes on a redirect are modified, does the database return them?"
    short_link = random_short_link(defaults.test_string_length)
    url = unsafe_random_string(defaults.test_string_length)
    response_status = int(defaults.test_string_length)
    body = unsafe_random_string(defaults.test_string_length)
    create_redirect_schema = RedirectCreate(
        short_link=short_link, url=url, response_status=response_status, body=body
    )

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )

    new_short_link = random_short_link(defaults.test_string_length)
    assert new_short_link != short_link
    new_url = unsafe_random_string(defaults.test_string_length)
    assert new_url != url
    new_response_status = abs(int(defaults.test_string_length) - 1)
    assert new_response_status != response_status
    new_body = unsafe_random_string(defaults.test_string_length)
    assert new_body != body

    update_redirect_schema = RedirectUpdate(
        short_link=new_short_link,
        url=new_url,
        response_status=new_response_status,
        body=new_body,
    )

    updated_redirect = await database_interface.redirect.update(
        in_memory_database,
        current_object_schema=created_redirect,
        update_object_schema=update_redirect_schema,
    )

    update_data = update_redirect_schema.dict()
    updated_redirect_data = updated_redirect.dict(exclude={"id"})
    assert updated_redirect_data == update_data


async def test_redirect_remove_by_id(in_memory_database: AsyncSession) -> None:
    "if a redirect is deleted, can their data no longer be found in the database?"
    create_redirect_schema = RedirectCreate()

    created_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=create_redirect_schema
    )

    retrieved_redirect = await database_interface.redirect.get_by_id(
        in_memory_database, id=created_redirect.id
    )
    assert retrieved_redirect == created_redirect

    removed_redirect = await database_interface.redirect.remove_by_id(
        in_memory_database, id=created_redirect.id
    )
    assert removed_redirect == created_redirect

    with pytest.raises(NoResultFound):
        _ = await database_interface.redirect.get_by_id(
            in_memory_database, id=created_redirect.id
        )
