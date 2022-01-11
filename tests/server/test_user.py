from fastapi.testclient import TestClient

from mw_url_shortener.schemas.security import AuthorizationHeaders
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
from tests.utils import random_password, random_username


def test_user_me(
    test_client: TestClient, authorization_headers: AuthorizationHeaders
) -> None:
    """
    can the user associated with the jwt be retrieved?

    also

    can the test client be used to interact with a secured endpoint?
    """
    me_response = test_client.get("/v0/user/me", headers=authorization_headers)
    assert me_response.status_code == 200
    me_data = me_response.text
    me = User.parse_raw(me_data)


def test_user_get_by_id(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    "can a user be retrieved by id?"
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
    "is an error returned if the user does not exist?"
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
    "can a user be created and retrieved?"
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
    """
    if all the attributes of a user are updated, can the new info be retrieved?
    """
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


def test_user_update_username(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    "if only the username is updated, can the updated info be retrieved?"
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

    user_update_schema = UserUpdate(username=new_username)
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


def test_user_update_non_existent(
    test_client: TestClient,
    authorization_headers: AuthorizationHeaders,
    test_user: User,
) -> None:
    "will an error be returned for a user update if the user doesn't exist?"
    username = random_username()
    assert username != test_user.username

    password = random_password()
    new_password = random_password()
    assert new_password != password

    user_schema = User(id=100_000, username=username, password=password)
    user_update_schema = UserUpdate(password=new_password)
    user_update_schema_data = user_update_schema.dict()
    original_user_data = user_schema.dict()
    update_body = {
        "current_object_schema": original_user_data,
        "update_object_schema": user_update_schema_data,
    }
    update_result = test_client.put(
        "/v0/user/", headers=authorization_headers, json=update_body
    )
    assert update_result.status_code == 409
