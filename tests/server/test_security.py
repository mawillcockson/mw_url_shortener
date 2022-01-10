"does authentication and authorization work with the api?"
from fastapi.testclient import TestClient

from mw_url_shortener.schemas.user import User
from mw_url_shortener.server.settings import server_defaults
from tests.utils import random_password, random_username


def test_token(test_client: TestClient, test_user: User, test_password: str) -> None:
    form_data = {
        "username": test_user.username,
        "password": test_password,
    }
    token_response = test_client.post(
        "/" + server_defaults.oauth2_endpoint, data=form_data
    )
    assert token_response.status_code == 200
    token_response_data = token_response.json()
    assert token_response_data
    assert "access_token" in token_response_data


def test_authenticate(
    test_client: TestClient, test_user: User, test_password: str
) -> None:
    form_data = {
        "username": test_user.username,
        "password": test_password,
    }
    token_response = test_client.post(
        "/" + server_defaults.oauth2_endpoint, data=form_data
    )
    assert token_response.status_code == 200
    token_response_data = token_response.json()
    assert token_response_data

    access_token = token_response_data["access_token"]
    headers = {"Authorization": "Bearer" + " " + access_token}
    me_response = test_client.get("/v0/user/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    me = User.parse_obj(me_data)
    assert me
    assert me == test_user


def test_token_invalid_user(
    test_client: TestClient, test_user: User, test_password: str
) -> None:
    invalid_username = random_username()
    assert invalid_username != test_user.username

    invalid_password = random_password()
    assert invalid_password != test_password

    form_data = {
        "username": invalid_username,
        "password": invalid_password,
    }
    response = test_client.post("/" + server_defaults.oauth2_endpoint, data=form_data)
    assert response.status_code == 401


def test_token_invalid_password(
    test_client: TestClient, test_user: User, test_password: str
) -> None:
    invalid_password = random_password()
    assert invalid_password != test_password

    form_data = {
        "username": test_user.username,
        "password": invalid_password,
    }
    response = test_client.post("/" + server_defaults.oauth2_endpoint, data=form_data)
    assert response.status_code == 401
