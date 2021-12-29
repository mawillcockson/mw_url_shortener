"""
does the database interface behave as expected?
"""
from re import escape
from typing import List

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.schemas.redirect import (
    Redirect,
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

    retrieved_redirects = await database_interface.redirect.search(
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

    retrieved_redirects = await database_interface.redirect.search(
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

    assert created_redirect.body is not None  # for mypy

    retrieved_redirects = await database_interface.redirect.search(
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


async def test_search_redirect_by_everything(in_memory_database: AsyncSession) -> None:
    """
    if many similar redirects are in the database, can a specific one be
    retrieved?
    """
    short_link = random_short_link(defaults.test_string_length)
    different_short_link1 = random_short_link(defaults.test_string_length)
    different_short_link2 = random_short_link(defaults.test_string_length)
    different_short_link3 = random_short_link(defaults.test_string_length)
    different_short_link4 = random_short_link(defaults.test_string_length)
    # affirm that all the short links are unique from each other
    assert (
        len(
            {
                short_link,
                different_short_link1,
                different_short_link2,
                different_short_link3,
                different_short_link4,
            }
        )
        == 5
    )

    url = unsafe_random_string(defaults.test_string_length)
    different_url = unsafe_random_string(defaults.test_string_length)
    assert url != different_url

    response_status = 1
    different_response_status = 2
    assert response_status != different_response_status

    body = unsafe_random_string(defaults.test_string_length)
    different_body = unsafe_random_string(defaults.test_string_length)
    assert body != different_body

    desired_redirect_schema = RedirectCreate(
        short_link=short_link, url=url, response_status=response_status, body=body
    )

    desired_redirect = await database_interface.redirect.create(
        in_memory_database, create_object_schema=desired_redirect_schema
    )
    assert desired_redirect

    redirect_different_short_link_schema = RedirectCreate(
        short_link=different_short_link1,
        url=url,
        response_status=response_status,
        body=body,
    )

    redirect_different_short_link = await database_interface.redirect.create(
        in_memory_database, create_object_schema=redirect_different_short_link_schema
    )
    assert redirect_different_short_link != desired_redirect

    similar_redirect_schema2 = RedirectCreate(
        short_link=different_short_link2,
        url=different_url,
        response_status=response_status,
        body=body,
    )

    similar_redirect_schema3 = RedirectCreate(
        short_link=different_short_link3,
        url=url,
        response_status=different_response_status,
        body=body,
    )

    similar_redirect_schema4 = RedirectCreate(
        short_link=different_short_link4,
        url=url,
        response_status=response_status,
        body=different_body,
    )

    other_similar_redirects: List[Redirect] = []
    for similar_redirect_schema in [
        similar_redirect_schema2,
        similar_redirect_schema3,
        similar_redirect_schema4,
    ]:
        similar_redirect = await database_interface.redirect.create(
            in_memory_database, create_object_schema=similar_redirect_schema
        )
        assert similar_redirect
        other_similar_redirects.append(similar_redirect)

    # affirm desired redirect is different in at least some way from each other
    # similar redirect
    assert desired_redirect not in other_similar_redirects

    retrieved_redirects = await database_interface.redirect.search(
        in_memory_database,
        # NOTE::FUTURE short_link has a UNIQUE constraint in the database
        # currently.
        # When this is removed, searching by short_link will be meaningfully
        # different from get_by_short_link or get_by_id.
        #
        # short_link=short_link,
        url=url,
        response_status=response_status,
        body=body,
    )
    assert len(retrieved_redirects) == 2, str(retrieved_redirects)
    assert desired_redirect in retrieved_redirects
    assert redirect_different_short_link in retrieved_redirects
