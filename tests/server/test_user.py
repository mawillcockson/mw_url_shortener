from fastapi.testclient import TestClient

from mw_url_shortener.schemas.security import AuthorizationHeaders
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
from tests.utils import random_password, random_username


def test_user_me(
    test_client: TestClient, authorization_headers: AuthorizationHeaders
) -> None:
    me_response = test_client.get("/v0/user/me", headers=authorization_headers)
    assert me_response.status_code == 200
    me_data = me_response.text
    me = User.parse_raw(me_data)


def test_user_get_by_id(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    params = {"id": test_user.id}
    retrieve_response = test_client.get(
        "/v0/user/", headers=authorization_headers, params=params
    )
    assert retrieve_response.status_code == 200
    retrieve_data = retrieve_response.text
    retrieved_user = User.parse_raw(retrieve_data)

    assert retrieved_user == test_user


def test_user_get_by_id_non_existent(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    id_ = 100_000
    assert id_ != test_user.id

    params = {"id": id_}
    retrieve_response = test_client.get(
        "/v0/user/", headers=authorization_headers, params=params
    )
    assert retrieve_response.status_code == 404


def test_user_roundtrip(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    username = random_username()
    assert username != test_user.username

    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    create_response = test_client.post(
        "/v0/user/", headers=authorization_headers, json=user_create_schema.dict()
    )
    assert create_response.status_code == 200
    create_data = create_response.text
    assert create_data
    created_user = User.parse_raw(create_data)

    params = {"id": created_user.id}
    retrieve_response = test_client.get(
        "/v0/user/", headers=authorization_headers, params=params
    )
    assert retrieve_response.status_code == 200
    retrieve_data = retrieve_response.json()
    retrieved_user = User.parse_obj(retrieve_data)

    assert retrieved_user == created_user


def test_user_update_full(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    username = random_username()
    assert username != test_user.username

    password = random_password()
    user_create_schema = UserCreate(username=username, password=password)
    create_response = test_client.post(
        "/v0/user/", headers=authorization_headers, json=user_create_schema.dict()
    )
    assert create_response.status_code == 200
    create_data = create_response.text
    assert create_data
    created_user = User.parse_raw(create_data)

    new_username = random_username()
    assert len({new_username, username, test_user.username}) == 3

    new_password = random_password()
    assert new_password != password

    user_update_schema = UserUpdate(username=new_username, password=new_password)
    user_update_schema_data = user_update_schema.dict()
    created_user_data = created_user.dict()
    update_body = {
        "current_object_schema": created_user_data,
        "update_object_schema": user_update_schema_data,
    }
    update_result = test_client.put(
        "/v0/user/", headers=authorization_headers, json=update_body
    )
    assert update_result.status_code == 200
    update_data = update_result.text
    assert update_data
    updated_user = User.parse_raw(update_data)

    params = {"id": created_user.id}
    retrieve_response = test_client.get(
        "/v0/user/", headers=authorization_headers, params=params
    )
    assert retrieve_response.status_code == 200
    retrieve_data = retrieve_response.json()
    retrieved_user = User.parse_obj(retrieve_data)

    assert retrieved_user == updated_user