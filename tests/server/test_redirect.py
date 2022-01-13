from typing import List

from fastapi.testclient import TestClient
from pydantic import parse_raw_as

from mw_url_shortener.schemas.redirect import (
    Redirect,
    RedirectCreate,
    RedirectUpdate,
    random_short_link,
)
from mw_url_shortener.schemas.security import AuthorizationHeaders
from mw_url_shortener.schemas.user import User
from mw_url_shortener.utils import unsafe_random_string


def test_redirect_create(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
    test_string_length: int,
) -> None:
    "can a redirect be created?"
    url = unsafe_random_string(test_string_length)
    short_link = random_short_link(test_string_length)
    response_status = int(test_string_length)
    body = unsafe_random_string(test_string_length)

    create_redirect_schema = RedirectCreate(
        url=url, short_link=short_link, response_status=response_status, body=body
    )

    create_response = test_client.post(
        "/v0/redirect/",
        headers=authorization_headers,
        json=create_redirect_schema.dict(),
    )
    assert create_response.status_code == 200
    create_data = create_response.text
    assert create_data
    created_redirect = Redirect.parse_raw(create_data)
    assert created_redirect.url == url
    assert created_redirect.short_link == short_link
    assert created_redirect.response_status == response_status
    assert created_redirect.body == body


def test_redirect_search_by_id(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
    test_string_length: int,
) -> None:
    "can a redirect be searched for only by id?"
    url = unsafe_random_string(test_string_length)
    other_url = unsafe_random_string(test_string_length)
    assert other_url != url

    short_link = random_short_link(test_string_length)
    other_short_link = random_short_link(test_string_length)
    assert other_short_link != short_link

    response_status = int(test_string_length)
    other_response_status = int(abs(test_string_length + 1))
    assert other_response_status != response_status

    body = unsafe_random_string(test_string_length)
    other_body = unsafe_random_string(test_string_length)
    assert other_body != body

    create_redirect_schema = RedirectCreate(
        url=url, short_link=short_link, response_status=response_status, body=body
    )

    other_redirect_schema = RedirectCreate(
        url=other_url,
        short_link=other_short_link,
        response_status=other_response_status,
        body=other_body,
    )

    create_response = test_client.post(
        "/v0/redirect/",
        headers=authorization_headers,
        json=create_redirect_schema.dict(),
    )
    assert create_response.status_code == 200
    create_data = create_response.text
    assert create_data
    created_redirect = Redirect.parse_raw(create_data)

    other_create_response = test_client.post(
        "/v0/redirect/",
        headers=authorization_headers,
        json=other_redirect_schema.dict(),
    )
    assert other_create_response.status_code == 200
    other_create_data = other_create_response.text
    assert other_create_data
    other_redirect = Redirect.parse_raw(other_create_data)

    params = {"id": created_redirect.id}
    search_response = test_client.get(
        "/v0/redirect/", headers=authorization_headers, params=params
    )
    assert search_response.status_code == 200
    search_data = search_response.text
    assert search_data
    retrieved_redirects = parse_raw_as(List[Redirect], search_data)
    assert created_redirect in retrieved_redirects
    assert len(retrieved_redirects) == 1


def test_redirect_search_non_existent(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    "will nothing be returned if no redirect matches search parameters?"
    params = {"id": 1}
    search_response = test_client.get(
        "/v0/redirect/", headers=authorization_headers, params=params
    )
    assert search_response.status_code == 200
    search_data = search_response.text
    assert search_data
    retrieved_redirects = parse_raw_as(List[Redirect], search_data)
    assert not retrieved_redirects


def test_redirect_update_all(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
    test_string_length: int,
) -> None:
    "if all attributes are updated, are the also returned?"
    url = unsafe_random_string(test_string_length)
    new_url = unsafe_random_string(test_string_length)
    assert new_url != url

    short_link = random_short_link(test_string_length)
    new_short_link = random_short_link(test_string_length)
    assert new_short_link != short_link

    response_status = int(test_string_length)
    new_response_status = int(abs(test_string_length + 1))
    assert new_response_status != response_status

    body = unsafe_random_string(test_string_length)
    new_body = unsafe_random_string(test_string_length)
    assert new_body != body

    create_redirect_schema = RedirectCreate(
        url=url, short_link=short_link, response_status=response_status, body=body
    )

    update_redirect_schema = RedirectUpdate(
        url=new_url,
        short_link=new_short_link,
        response_status=new_response_status,
        body=new_body,
    )

    create_response = test_client.post(
        "/v0/redirect/",
        headers=authorization_headers,
        json=create_redirect_schema.dict(),
    )
    assert create_response.status_code == 200
    create_data = create_response.text
    assert create_data
    created_redirect = Redirect.parse_raw(create_data)

    created_redirect_data = created_redirect.dict()
    update_redirect_data = update_redirect_schema.dict()
    update_data = {
        "current_object_schema": created_redirect_data,
        "update_object_schema": update_redirect_data,
    }
    update_response = test_client.put(
        "/v0/redirect/",
        headers=authorization_headers,
        json=update_data,
    )
    assert update_response.status_code == 200
    update_json = update_response.text
    assert update_json
    updated_redirect = Redirect.parse_raw(update_json)

    assert updated_redirect.url == new_url
    assert updated_redirect.short_link == new_short_link
    assert updated_redirect.response_status == new_response_status
    assert updated_redirect.body == new_body


def test_update_non_existent(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
    test_string_length: int,
) -> None:
    "will an error be returned if the specified redirect doesn't exist?"
    url = unsafe_random_string(test_string_length)
    new_url = unsafe_random_string(test_string_length)
    assert new_url != url

    short_link = random_short_link(test_string_length)
    new_short_link = random_short_link(test_string_length)
    assert new_short_link != short_link

    response_status = int(test_string_length)
    new_response_status = int(abs(test_string_length + 1))
    assert new_response_status != response_status

    body = unsafe_random_string(test_string_length)
    new_body = unsafe_random_string(test_string_length)
    assert new_body != body

    non_existent_redirect = Redirect(
        id=1,
        url=url,
        short_link=short_link,
        response_status=response_status,
        body=body,
    )

    update_redirect_schema = RedirectUpdate(
        url=new_url,
        short_link=new_short_link,
        response_status=new_response_status,
        body=new_body,
    )
    non_existent_redirect_data = non_existent_redirect.dict()
    update_redirect_data = update_redirect_schema.dict()
    update_data = {
        "current_object_schema": non_existent_redirect_data,
        "update_object_schema": update_redirect_data,
    }
    update_response = test_client.put(
        "/v0/redirect/",
        headers=authorization_headers,
        json=update_data,
    )
    assert update_response.status_code == 409


def test_redirect_remove_by_id(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
    test_string_length: int,
) -> None:
    "can a redirect be removed only by id?"
    url = unsafe_random_string(test_string_length)
    short_link = random_short_link(test_string_length)
    response_status = int(test_string_length)
    body = unsafe_random_string(test_string_length)

    create_redirect_schema = RedirectCreate(
        url=url, short_link=short_link, response_status=response_status, body=body
    )

    create_response = test_client.post(
        "/v0/redirect/",
        headers=authorization_headers,
        json=create_redirect_schema.dict(),
    )
    assert create_response.status_code == 200
    create_data = create_response.text
    assert create_data
    created_redirect = Redirect.parse_raw(create_data)

    params = {"id": created_redirect.id}
    remove_response = test_client.delete(
        "/v0/redirect/", headers=authorization_headers, params=params
    )
    assert remove_response.status_code == 200
    remove_data = remove_response.text
    assert remove_data
    removed_redirect = Redirect.parse_raw(remove_data)

    assert removed_redirect == created_redirect


def test_redirect_remove_by_id_non_existent(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    """
    will an error be raised if removal is requested for a redirect that doesn't
    exist?
    """
    params = {"id": 1}
    remove_response = test_client.delete(
        "/v0/redirect/", headers=authorization_headers, params=params
    )
    assert remove_response.status_code == 404
