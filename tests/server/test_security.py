"does authentication and authorization work with the api?"
import pydantic
import pytest
from fastapi.testclient import TestClient

from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
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

    with pytest.raises(pydantic.ValidationError):
        assert not User(id=1, username=username)
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]["type"] == "value_error.any_str.min_length"

    with pytest.raises(pydantic.ValidationError):
        assert not UserCreate(username=username, password=password)
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]["type"] == "value_error.any_str.min_length"

    with pytest.raises(pydantic.ValidationError):
        assert not UserUpdate(username=username, password=password)
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]["type"] == "value_error.any_str.min_length"
