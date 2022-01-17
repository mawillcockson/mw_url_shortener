"does authentication and authorization work with the api?"
import pydantic
import pytest
from fastapi.testclient import TestClient

from mw_url_shortener.schemas.security import AccessToken, make_authorization_headers
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
from mw_url_shortener.server.settings import server_defaults
from tests.utils import random_password, random_username


def test_retrieve_token(
    test_client: TestClient, test_user: User, test_password: str
) -> None:
    form_data = {
        "username": test_user.username,
        "password": test_password,
    }
    token_response = test_client.post("/v0/security/token", data=form_data)
    assert token_response.status_code == 200
    token_response_data = token_response.text
    assert token_response_data
    access_token = AccessToken.parse_raw(token_response_data)
    assert access_token.access_token


def test_authenticate(
    test_client: TestClient, test_user: User, test_password: str
) -> None:
    form_data = {
        "username": test_user.username,
        "password": test_password,
    }
    token_response = test_client.post("/v0/security/token", data=form_data)
    assert token_response.status_code == 200
    token_response_data = token_response.text
    assert token_response_data

    access_token = AccessToken.parse_raw(token_response_data)
    headers = make_authorization_headers(token=access_token.access_token)
    me_response = test_client.get("/v0/user/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.text
    assert me_data
    me = User.parse_raw(me_data)
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
    response = test_client.post("/v0/security/token", data=form_data)
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
    response = test_client.post("/v0/security/token", data=form_data)
    assert response.status_code == 401


# DONE:SECURITY:OAUTH2
# FastAPI does not allow empty passwords or usernames with the OAuth2 scheme
# this app uses.
# This is because the OAuth2PasswordRequestForm specific Form(...) for the
# username and password fields it requires:
# https://github.com/tiangolo/fastapi/blob/672c55ac626b20cc6219696023cdcc5871e5141d/fastapi/security/oauth2.py#L49-L50
#
# and then Form(...) is taken to mean that a value cannot be an empty string:
# https://github.com/tiangolo/fastapi/blob/672c55ac626b20cc6219696023cdcc5871e5141d/fastapi/dependencies/utils.py#L651
#
# These seem reasonable. It could be possible to override the behaviour by
# subclassing OAuth2PasswordRequestForm and specifying the default value as an
# empty string, but this would allow an a form that doesn't include the
# password field, to be treated the same as one that sets it to be empty.
# Semantically, that wouldn't be too different, but it's easier, and definitely
# slightly more secure, to ensure empty passwords and usernames can't be used.


def test_empty_password() -> None:
    "will working with a user with an empty password raise an error?"
    username = random_username()
    password = ""

    with pytest.raises(pydantic.ValidationError) as error:
        assert not UserCreate(username=username, password=password)
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]["type"] == "value_error.any_str.min_length"

    with pytest.raises(pydantic.ValidationError) as error:
        assert not UserUpdate(username=username, password=password)
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]["type"] == "value_error.any_str.min_length"


def test_empty_username() -> None:
    "will working with a user with an empty username raise an error?"
    username = ""
    password = random_password()

    with pytest.raises(pydantic.ValidationError) as error:
        assert not User(id=1, username=username)
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]["type"] == "value_error.any_str.min_length"

    with pytest.raises(pydantic.ValidationError) as error:
        assert not UserCreate(username=username, password=password)
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]["type"] == "value_error.any_str.min_length"

    with pytest.raises(pydantic.ValidationError) as error:
        assert not UserUpdate(username=username, password=password)
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]["type"] == "value_error.any_str.min_length"
