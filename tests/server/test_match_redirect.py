from urllib.parse import unquote

from fastapi.testclient import TestClient

from mw_url_shortener.schemas.redirect import (
    Redirect,
    RedirectCreate,
    random_short_link,
)
from mw_url_shortener.schemas.security import AuthorizationHeaders
from mw_url_shortener.schemas.user import User
from mw_url_shortener.utils import unsafe_random_string


def test_match_short_link(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
    test_string_length: int,
) -> None:
    "can a redirect be matched by short_link only?"
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

    match_response = test_client.get(
        "/v0/redirect/match/" + short_link, headers=authorization_headers
    )
    assert match_response.status_code == response_status
    assert "location" in match_response.headers
    quoted_redirect_url = match_response.headers["location"]
    redirect_url = unquote(quoted_redirect_url)
    assert redirect_url == url
    decoded_content = match_response.text
    assert decoded_content == body
