from pathlib import Path
from typing import Iterator

import inject
import pytest
from fastapi.testclient import TestClient

from mw_url_shortener.database.start import make_sessionmaker
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.schemas.security import (
    AccessToken,
    AuthorizationHeaders,
    OAuth2PasswordRequestFormData,
    make_authorization_headers,
)
from mw_url_shortener.schemas.user import User, UserCreate
from mw_url_shortener.server.app import make_fastapi_app
from mw_url_shortener.server.settings import ServerSettings, server_defaults
from mw_url_shortener.settings import defaults
from mw_url_shortener.utils import safe_random_string
from tests.utils import random_password, random_username


@pytest.fixture
def test_password() -> str:
    return random_password()


@pytest.fixture
def test_user_schema(test_password: str) -> UserCreate:
    test_username = random_username()
    return UserCreate(username=test_username, password=test_password)


@pytest.fixture
async def test_user(
    anyio_backend: str, empty_on_disk_database: Path, test_user_schema: UserCreate
) -> User:
    assert anyio_backend

    database_url = defaults.database_url_leader + str(empty_on_disk_database)
    async_sessionmaker = await make_sessionmaker(database_url)
    async with async_sessionmaker() as async_session:
        test_user = await database_interface.user.create(
            async_session, create_object_schema=test_user_schema
        )

    assert test_user
    return test_user


@pytest.fixture
def test_client(test_user: User, empty_on_disk_database: Path) -> Iterator[TestClient]:
    # safe_random_string takes a length in bytes, and the output string is in
    # hexadecimal, with each byte converted to two hexadecimal digits:
    # https://docs.python.org/3/library/secrets.html#secrets.token_hex
    jwt_secret_key = safe_random_string(server_defaults.jwt_secret_key_max_length // 2)
    server_settings = ServerSettings(
        database_path=empty_on_disk_database, jwt_secret_key=jwt_secret_key
    )
    app = make_fastapi_app(server_settings)
    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        inject.clear()


@pytest.fixture
def authorization_headers(
    test_client: TestClient, test_user: User, test_password: str
) -> AuthorizationHeaders:
    form_data = OAuth2PasswordRequestFormData(
        username=test_user.username,
        password=test_password,
    )
    token_response = test_client.post(
        "/" + server_defaults.oauth2_endpoint, data=form_data
    )
    assert token_response.status_code == 200
    token_response_data = token_response.text
    assert token_response_data

    access_token = AccessToken.parse_raw(token_response_data)
    return make_authorization_headers(token=access_token.access_token)
