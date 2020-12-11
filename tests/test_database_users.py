from mw_url_shortener.database import user
from mw_url_shortener.database.errors import UserNotFoundError
from mw_url_shortener.types import HashedPassword
import pytest
from pony.orm import Database


def test_create_user(database: Database, example_user: user.Model) -> None:
    "can a user be added and read back"
    created_user = user.create(db=database, user=example_user)
    returned_user = user.get(db=database, username=created_user.username)
    assert returned_user == created_user


# NOTE:BUG I want to be able to request multiple example users
# pytest currently does not have a builtin way to call a fixture multiple time,
# but # NOTE:FUTURE on that:
# https://github.com/pytest-dev/pytest/issues/2703
# Currently, I'm creating a new user by manually requesting more components for
# a new user
def test_create_duplicate_user(database: Database, example_user: user.Model, example_hashed_password: HashedPassword) -> None:
    "is an error raised if a username is already taken"
    raise NotImplementedError


def test_update_user(database: Database, example_user: user.Model, example_hashed_password: HashedPassword) -> None:
    "can an existing user be modified"
    assert example_user.hashed_password != example_hashed_password, "hashed_password does not change; user properties must change during update"
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

# NOTE:BUG I want to be able to request multiple example users
# pytest currently does not have a builtin way to call a fixture multiple time,
# but # NOTE:FUTURE on that:
# https://github.com/pytest-dev/pytest/issues/2703
# Currently, I'm creating a new user by manually requesting more components for
# a new user
def test_update_deleted_user(database: Database, example_user: user.Model, example_hashed_password: HashedPassword) -> None:
    """
    is an error raised when an update is performed on a user that doesn't exist
    """
    raise NotImplementedError


def test_delete_user(database: Database, example_user: user.Model) -> None:
    """
    if a user is deleted, are the removed from the list of users,
    and is an error raised when a unique id is used to retriece it
    """
    created_user = user.create(db=database, user=example_user)
    user.delete(db=database, username=returned_user.username)
    users = user.list(db=database)
    for u in users:
        assert u != created_user
    with pytest.raises(UserNotFoundError) as err:
        user.get(db=database, username=created_user.username)
    assert f"no user found with username '{created_user.username}'" in str(err.value)


def test_delete_nonexistent_user(database: Database, example_user: user.Model) -> None:
    """
    is an error raised when a deletion is performed on a user that doesn't
    exist
    """
    raise NotImplementedError
