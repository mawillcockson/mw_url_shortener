"""
tests the user part of the database interface
"""
from mw_url_shortener.database import user
from mw_url_shortener.database.errors import UserNotFoundError, UserAlreadyExistsError, DatabaseError
from mw_url_shortener.types import HashedPassword
import pytest
from pony.orm import Database
from .utils import random_user, random_hashed_password, random_username


def test_create_user(database: Database) -> None:
    "can a user be added and read back"
    example_user: user.Model = random_user()

    created_user = user.create(db=database, user=example_user)
    returned_user = user.get(db=database, username=created_user.username)
    assert returned_user == created_user


# DONE:NOTE:BUG I want to be able to request multiple example users
# pytest currently does not have a builtin way to call a fixture multiple time,
# but # DONE:NOTE:FUTURE on that:
# https://github.com/pytest-dev/pytest/issues/2703
# Currently, I'm creating a new user by manually requesting more components for
# a new user
# DONE:
# Created tests.utils.py to assist with generating test data
# This was necessary anyways, since unfortunately, the function-scoped pytest
# fixtures are kept throught the whole run of a single test_ function. This
# means that the assertion that the hashed passwords are different was
# consistently failing.
def test_create_duplicate_user(database: Database) -> None:
    "is an error raised if a username is already taken"
    example_user: user.Model = random_user()
    example_hashed_password: HashedPassword = random_hashed_password()
    assert example_user.hashed_password != example_hashed_password, "passwords need to be different"

    created_user = user.create(db=database, user=example_user)
    duplicate_user = created_user.copy(update={"hashed_password": example_hashed_password})
    with pytest.raises(UserAlreadyExistsError) as err:
        user.create(db=database, user=duplicate_user)
    assert f"a user with username '{duplicate_user.username}' already exists" in str(err.value)


@pytest.mark.xfail
def test_create_duplicate_password(database: Database) -> None:
    "can a user be created with a password that's the same as another user"
    raise NotImplementedError


def test_update_user(database: Database) -> None:
    "can an existing user be modified"
    example_user: user.Model = random_user()
    example_hashed_password: HashedPassword = random_hashed_password()
    assert example_user.hashed_password != example_hashed_password, "passwords need to be different"

    # NOTE:IMPLEMENTATION::USERS In the future, I may want to use something other than
    # the username of a user as the uniquely primary key in the database.
    # This would allow changing the username.
    # Currently, to change the username, a new user has to be created, and the old one deleted.
    # To facilitate a future where user ids may not be the username, the
    # interfce described in this test uses the username as the user id
    # explicitly, as opposed to expecting the user functions to implicitly look
    # at the username attribute of the passed in user.
    # It's also why the flow is:
    # - Get the current user model for the user
    # - Make a copy, updating the properties at the same time
    # - Update the user in the database, using the user id returned with the
    #   first user model to identify which user the model should be applied to
    # The functions could implicitly look at the user id of a model that has one. I'll see about it when it's implemented
    created_user = user.create(db=database, user=example_user)
    updated_user = created_user.copy(update={"hashed_password": example_hashed_password})
    user.update(db=database, username=created_user.username, updated_user=updated_user)
    returned_updated_user = user.get(db=database, username=created_user.username)
    assert returned_updated_user == updated_user


def test_delete_user(database: Database) -> None:
    """
    if a user is deleted, are they removed from the list of users,
    and is an error raised when a unique id is used to retrieve it
    """
    example_user: user.Model = random_user()

    created_user = user.create(db=database, user=example_user)
    user.delete(db=database, user=created_user)
    users = user.list(db=database)
    for usr in users:
        assert usr != created_user
    with pytest.raises(UserNotFoundError) as err:
        user.get(db=database, username=created_user.username)
    assert f"no user found with username '{created_user.username}'" in str(err.value)


def test_delete_nonexistent_user(database: Database) -> None:
    """
    is an error raised when a deletion is performed on a user that doesn't
    exist
    """
    example_user: user.Model = random_user()
    
    with pytest.raises(UserNotFoundError) as err:
        user.delete(db=database, user=example_user)
    assert f"no user found with username '{example_user.username}'" in str(err.value)


def test_user_duplicate_deletion(database: Database) -> None:
    "is an error raised when a user is deleted a second time"
    example_user: user.Model = random_user()
    
    created_user = user.create(db=database, user=example_user)
    user.delete(db=database, user=created_user)
    with pytest.raises(UserNotFoundError) as err:
        user.delete(db=database, user=example_user)
    assert f"no user found with username '{example_user.username}'" in str(err.value)


def test_update_deleted_user(database: Database) -> None:
    """
    is an error raised when an update is performed on a user that doesn't exist
    """
    example_user: user.Model = random_user()
    example_hashed_password: HashedPassword = random_hashed_password()
    assert example_user.hashed_password != example_hashed_password, "passwords need to be different"

    created_user = user.create(db=database, user=example_user)
    user.delete(db=database, user=created_user)
    updated_user = created_user.copy(update={"hashed_password": example_hashed_password})
    with pytest.raises(UserNotFoundError) as err:
        user.update(db=database, username=updated_user.username, updated_user=updated_user)
    assert f"no user found with username '{updated_user.username}'" in str(err.value)


@pytest.mark.xfail
def test_delete_user_by_username() -> None:
    "can a user be deleted by username"
    raise NotImplementedError


@pytest.mark.xfail
def test_delete_nonmatching_user() -> None:
    """
    is an error raised if a deletion is requested for a user model that doesn't
    match what's in the database
    """
    raise NotImplementedError
