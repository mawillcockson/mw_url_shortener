from fastapi.testclient import TestClient

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
