from typing import List

from fastapi.testclient import TestClient
from pydantic import parse_raw_as

from mw_url_shortener.schemas.redirect import (
    Redirect,
    RedirectCreate,
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
